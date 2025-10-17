from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

import httpx

from .logging import get_logger


logger = get_logger(__name__)


def _load_provider_config() -> dict:
    cfg_path = os.getenv("PROVIDERS_CONFIG", os.path.join(os.getcwd(), "configs", "providers.toml"))
    try:
        import tomllib  # py311+
    except ModuleNotFoundError:  # pragma: no cover
        import tomli as tomllib  # type: ignore
    if not os.path.exists(cfg_path):
        return {}
    with open(cfg_path, "rb") as f:
        return tomllib.load(f)


def _get_llm_provider() -> str:
    return (os.getenv("LLM_PROVIDER") or _load_provider_config().get("llm", {}).get("provider") or "").lower()


def _read_key_from_file(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def _get_openai_key() -> Optional[str]:
    return os.getenv("OPENAI_API_KEY") or _read_key_from_file("/keys/OPENAI_API_KEY")


def _openai_reason(claim_text: str, evidence: List[Dict[str, Any]], model: str = "gpt-4o-mini") -> Optional[Dict[str, Any]]:
    api_key = _get_openai_key()
    if not api_key:
        logger.info("OPENAI_API_KEY not found; skipping LLM reasoning")
        return None

    sys_prompt = (
        "You are a precise fact-checking assistant. Based ONLY on the provided evidence, "
        "write concise reasons and suggest a truth probability. Do not include chain-of-thought. "
        "Return strictly a JSON object with keys: reasons (array of 2-4 short strings), "
        "suggested_score (number 0..1)."
    )
    content = {
        "claim": claim_text,
        "evidence": [
            {"url": e.get("url"), "title": e.get("title"), "quote": e.get("quote"), "credibility": e.get("credibility")}
            for e in evidence
        ],
    }
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": json.dumps(content, ensure_ascii=False)},
    ]
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": os.getenv("OPENAI_MODEL", model),
        "messages": messages,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    try:
        with httpx.Client(timeout=20.0) as client:
            resp = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()
            txt = data["choices"][0]["message"]["content"]
            return json.loads(txt)
    except Exception as e:
        logger.warning("OpenAI reasoning failed: %s", e)
        return None


def reason_claim(claim_text: str, evidence: List[Dict[str, Any]]) -> Tuple[List[str], Optional[float]]:
    """Try to get LLM-backed reasons and an optional score suggestion.

    Returns (reasons, suggested_score). If LLM not available or fails, returns ([], None).
    """
    provider = _get_llm_provider()
    if provider != "openai":
        return [], None
    out = _openai_reason(claim_text, evidence)
    if not out:
        return [], None
    reasons = out.get("reasons") or []
    score = out.get("suggested_score")
    try:
        score = float(score) if score is not None else None
    except Exception:
        score = None
    # Truncate reasons lengths conservatively
    reasons = [str(r)[:240] for r in reasons][:5]
    return reasons, score

