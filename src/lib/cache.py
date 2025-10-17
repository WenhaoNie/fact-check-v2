from __future__ import annotations

import time
from functools import wraps
from typing import Any, Callable, Dict, Hashable, Optional, Tuple


class TTLCache:
    def __init__(self, default_ttl: float = 600.0) -> None:
        self.default_ttl = default_ttl
        self._store: Dict[Hashable, Tuple[float, Any]] = {}

    def get(self, key: Hashable) -> Optional[Any]:
        now = time.time()
        rec = self._store.get(key)
        if not rec:
            return None
        exp, val = rec
        if exp < now:
            self._store.pop(key, None)
            return None
        return val

    def set(self, key: Hashable, value: Any, ttl: Optional[float] = None) -> None:
        exp = time.time() + (ttl if ttl is not None else self.default_ttl)
        self._store[key] = (exp, value)


_GLOBAL_CACHE = TTLCache()


def memoize_ttl(ttl: float):
    def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = (fn.__module__, fn.__name__, args, tuple(sorted(kwargs.items())))
            val = _GLOBAL_CACHE.get(key)
            if val is not None:
                return val
            out = fn(*args, **kwargs)
            _GLOBAL_CACHE.set(key, out, ttl)
            return out

        return wrapper

    return deco

