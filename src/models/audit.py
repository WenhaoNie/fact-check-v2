from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolTrace(BaseModel):
    step: int
    action: str
    args: Dict[str, Any] = Field(default_factory=dict)
    ok: bool = True
    latency_ms: Optional[int] = None
    error: Optional[str] = None


class Usage(BaseModel):
    tokens_prompt: Optional[int] = None
    tokens_completion: Optional[int] = None
    duration_ms: Optional[int] = None


class AuditInfo(BaseModel):
    generated_at: str
    tool_traces: List[ToolTrace] = Field(default_factory=list)
    usage: Usage = Field(default_factory=Usage)

