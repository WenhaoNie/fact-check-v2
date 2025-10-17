from __future__ import annotations

from typing import Any, Dict

from ..lib.logging import get_logger


logger = get_logger(__name__)


def verify_claim(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Service entrypoint: verify a claim and return a structured judgment.

    Skeleton only. Full orchestration (pipelines, search, fetch, policy, LLM)
    will be implemented in User Story phases.
    """
    raise NotImplementedError("verify_claim orchestration not implemented yet")


# Maintain contract-driven TDD by failing import in integration tests until
# User Story 1 wires the service. This avoids false greens before pipelines
# are ready.
raise RuntimeError("VerificationService not wired yet (Phase 2)")

