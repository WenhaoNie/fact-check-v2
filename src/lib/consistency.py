from __future__ import annotations

from typing import Literal


Binary = Literal["yes", "no", "unknown"]


def hysteresis_binary(score: float, *, threshold: float = 0.5, margin: float = 0.05) -> Binary:
    """Map a probability to a stable binary with a deadband around threshold.

    - score >= threshold + margin → "yes"
    - score <= threshold - margin → "no"
    - otherwise → "unknown" (avoid flip-flops)
    """
    if score >= threshold + margin:
        return "yes"
    if score <= threshold - margin:
        return "no"
    return "unknown"

