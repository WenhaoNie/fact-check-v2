from __future__ import annotations

import random
import time
from functools import wraps
from typing import Any, Callable, Type, Tuple

from .logging import get_logger


logger = get_logger(__name__)


Retryable = (ConnectionError,)  # broaden as needed


def with_retries(
    max_attempts: int = 3,
    base_delay: float = 0.5,
    jitter: float = 0.1,
    retry_on: Tuple[Type[BaseException], ...] = (Exception,),
):
    """Decorator adding ≤(max_attempts-1) retries with exponential backoff.

    Default attempts=3 → at most 2 retries.
    """

    def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except retry_on as e:  # type: ignore[misc]
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.warning("Retry attempts exhausted: %s", e)
                        raise
                    delay = (2 ** (attempt - 1)) * base_delay
                    delay += random.uniform(0, jitter)
                    logger.info("Retrying (%d/%d) after %.2fs due to: %s", attempt, max_attempts - 1, delay, e)
                    time.sleep(delay)

        return wrapper

    return deco

