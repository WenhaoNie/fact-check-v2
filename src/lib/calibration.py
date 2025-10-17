from __future__ import annotations

from typing import Optional


def calibrate(score: Optional[float]) -> Optional[float]:
    """Calibrate the input probability score.

    Placeholder: identity function for MVP. Hook for quarterly calibration
    updates loaded from persisted artifacts in future iterations.
    """
    return score

