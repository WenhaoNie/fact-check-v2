import logging
import os
from typing import Optional


REDACT_KEYS = {"API_KEY", "ACCESS_KEY", "SECRET", "TOKEN", "PASSWORD"}


def _redact(msg: str) -> str:
    for k in REDACT_KEYS:
        v = os.environ.get(k)
        if v and v in msg:
            msg = msg.replace(v, "***")
    return msg


class RedactingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        raw = super().format(record)
        return _redact(raw)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name or "factcheck")
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = os.getenv("LOG_FORMAT", "%(asctime)s %(levelname)s %(name)s: %(message)s")
        handler.setFormatter(RedactingFormatter(fmt))
        logger.addHandler(handler)
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, level, logging.INFO))
    logger.propagate = False
    return logger

