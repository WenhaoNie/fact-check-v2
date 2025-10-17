from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field, HttpUrl, conlist, confloat
from .audit import AuditInfo


Locale = Literal["zh", "en", "auto"]
Credibility = Literal["authority", "registry", "web", "limited"]
Kind = Literal["binary", "continuous", "both"]
Binary = Literal["yes", "no", "unknown"]


class Claim(BaseModel):
    id: Optional[str] = None
    subject: Optional[str] = None
    text: Optional[str] = None
    time_window: Optional[str] = None
    locale: Locale = "auto"
    notes: Optional[str] = None


class EvidenceItem(BaseModel):
    url: HttpUrl
    title: str
    quote: str
    fetched_at: str
    credibility: Optional[Credibility] = None


class Judgment(BaseModel):
    kind: Kind = "both"
    binary: Optional[Binary] = None
    score: Optional[confloat(ge=0.0, le=1.0)] = None
    reasons: conlist(str, min_length=1, max_length=5)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    missing_candidates: List[str] = Field(default_factory=list)
    suspicious_items: List[str] = Field(default_factory=list)
    audit: AuditInfo

