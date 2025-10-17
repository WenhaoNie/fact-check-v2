from __future__ import annotations

from typing import Any, Dict

from lib.logging import get_logger
from services.pipeline_text import run as run_text
from services.pipeline_structured import run as run_structured
from lib.calibration import calibrate
from lib.consistency import hysteresis_binary
from lib.policy import evaluate_evidence_credibility, DEFAULT_THRESHOLD
from models.schemas import Judgment


logger = get_logger(__name__)


def verify_claim(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Service entrypoint: verify a claim and return a structured judgment.

    Supports text input for US1. Structured input to be added in US2.
    """
    input_obj = payload.get("input") or {}
    output_obj = payload.get("output") or {}
    input_type = (input_obj.get("type") or "text").lower()
    output_kind = output_obj.get("kind") or "both"

    if input_type == "text":
        judgment = run_text(input_obj, output_kind=output_kind)
        _attach_continuous_score(judgment, input_obj)
        return {"judgment": judgment.model_dump(mode="json")}  # JSON-friendly types

    if input_type == "structured":
        judgment = run_structured(input_obj, output_kind=output_kind)
        _attach_continuous_score(judgment, input_obj)
        return {"judgment": judgment.model_dump(mode="json")}

    raise ValueError("Unsupported input.type; expected 'text' or 'structured'")


def _extract_llm_suggested_score(j: Judgment) -> float | None:
    try:
        for t in j.audit.tool_traces:
            if getattr(t, "action", None) == "llm_reason" and t.ok:
                s = (t.args or {}).get("suggested_score")
                if s is not None:
                    return float(s)
    except Exception:
        return None
    return None


def _extract_llm_stance(j: Judgment) -> str | None:
    try:
        for t in j.audit.tool_traces:
            if getattr(t, "action", None) == "llm_reason" and t.ok:
                stance = (t.args or {}).get("stance")
                if isinstance(stance, str):
                    stance = stance.lower()
                    if stance in {"support", "refute", "uncertain"}:
                        return stance
    except Exception:
        return None
    return None

def _attach_continuous_score(j: Judgment, input_obj: dict) -> None:
    """Compute a heuristic raw score, calibrate, and optionally map to binary.

    Conservative: keep existing binary if set by pipeline; otherwise map using
    hysteresis with default threshold. Always set score when output asks for it.
    """
    # If pipeline chose a binary already, we still compute score but keep binary.
    # Heuristic raw score from evidence credibility count
    creds = [e.credibility or "web" for e in j.evidence]
    has_auth = any(c in {"authority", "registry"} for c in creds)
    policy = evaluate_evidence_credibility(creds)

    if not j.evidence:
        raw = 0.2
    elif has_auth:
        raw = 0.65
    else:
        raw = 0.45

    llm_s = _extract_llm_suggested_score(j)
    llm_stance = _extract_llm_stance(j)
    if llm_s is not None:
        raw = 0.7 * raw + 0.3 * float(llm_s)

    j.score = calibrate(raw)

    # Tune binary mapping with LLM stance:
    # - If authority/registry present → map via hysteresis
    # - Else if LLM stance strong (support/refute) and score far from threshold → map
    # - Else keep unknown
    thr = DEFAULT_THRESHOLD
    margin = 0.05
    if policy.sufficient:
        j.binary = hysteresis_binary(float(j.score), threshold=thr, margin=margin)
    elif llm_s is not None and llm_stance in {"support", "refute"} and (llm_s >= thr + 0.1 or llm_s <= thr - 0.1):
        j.binary = hysteresis_binary(float(j.score), threshold=thr, margin=margin)
    else:
        # Keep pipeline's value (likely 'unknown')
        if j.binary is None:
            j.binary = "unknown"

    # Heuristic stance fallback when authority present but no LLM stance
    if policy.sufficient and llm_stance is None:
        neg_terms = [
            "not visible",
            "can't be seen",
            "cannot be seen",
            "myth",
            "谣言",
            "并非",
            "不可见",
        ]
        pos_terms = [
            "confirmed",
            "announced",
            "press release",
            "declared",
            "发布",
            "宣布",
        ]
        text = " ".join([(e.quote or "").lower() for e in j.evidence])
        if any(t in text for t in neg_terms):
            j.binary = "no"
            # Nudge score lower to reflect refutation
            j.score = calibrate(min(float(j.score or 0.5), thr - 0.15))
        elif any(t in text for t in pos_terms):
            j.binary = "yes"
            j.score = calibrate(max(float(j.score or 0.5), thr + 0.15))
