from __future__ import annotations

from typing import Any, Dict

from lib.logging import get_logger
from services.pipeline_text import run as run_text
from services.pipeline_structured import run as run_structured


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
        return {"judgment": judgment.model_dump()}  # pydantic to dict

    if input_type == "structured":
        judgment = run_structured(input_obj, output_kind=output_kind)
        return {"judgment": judgment.model_dump()}

    raise ValueError("Unsupported input.type; expected 'text' or 'structured'")
