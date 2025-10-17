from __future__ import annotations

from typing import Any, Dict

from lib.logging import get_logger
from services.pipeline_text import run as run_text
from services.pipeline_structured import run as run_structured
from lib.calibration import calibrate
from lib.consistency import hysteresis_binary
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


def _attach_continuous_score(j: Judgment, input_obj: dict) -> None:
    """Compute a heuristic raw score, calibrate, and optionally map to binary.

    Conservative: keep existing binary if set by pipeline; otherwise map using
    hysteresis with default threshold. Always set score when output asks for it.
    """
    # If pipeline chose a binary already, we still compute score but keep binary.
    # Heuristic raw score from evidence credibility count
    creds = [e.credibility or "web" for e in j.evidence]
    has_auth = any(c in {"authority", "registry"} for c in creds)
    if not j.evidence:
        raw = 0.2
    elif has_auth:
        raw = 0.6
    else:
        raw = 0.45
    j.score = calibrate(raw)
    # Only adjust binary if it is None; keep 'unknown' from pipeline as-is
    if j.binary is None:
        j.binary = hysteresis_binary(float(j.score))
