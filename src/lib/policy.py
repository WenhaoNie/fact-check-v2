from __future__ import annotations

from typing import Iterable, Tuple

from .logging import get_logger


logger = get_logger(__name__)


class PolicyResult:
    def __init__(self, sufficient: bool, limited_trust: bool, reason: str = "") -> None:
        self.sufficient = sufficient
        self.limited_trust = limited_trust
        self.reason = reason

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"PolicyResult(sufficient={self.sufficient}, limited_trust={self.limited_trust}, reason={self.reason!r})"


DEFAULT_THRESHOLD = 0.5  # Guidance: default decision threshold for binary mapping


def evaluate_evidence_credibility(credibilities: Iterable[str]) -> PolicyResult:
    """Apply evidence policy:

    - If at least one item is from `authority` or `registry` → sufficient.
    - Else if only `web/limited` present → insufficient, but limited trust flag.
    - If no evidence → insufficient.
    """
    creds = list(credibilities)
    if not creds:
        return PolicyResult(False, False, "no evidence available")

    if any(c in {"authority", "registry"} for c in creds):
        return PolicyResult(True, False, "contains authoritative/registry source")

    # Only general web sources
    return PolicyResult(False, True, "only general web sources; 可信度有限")
