from __future__ import annotations

from typing import Any, Dict, Tuple

from lib.auth import require_api_key
from lib.logging import get_logger
from services.verification_service import verify_claim


logger = get_logger(__name__)


def handle_verify_request(body: Dict[str, Any], headers: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    """Handle a POST /v1/verify request.

    This is a framework-agnostic handler returning (status_code, json_body).
    """
    try:
        require_api_key(headers)
    except PermissionError as e:
        return 401, {"error": str(e)}

    try:
        result = verify_claim(body)
        return 200, result
    except ValueError as e:
        return 400, {"error": str(e)}
    except Exception as e:
        logger.exception("verify handler failed: %s", e)
        return 500, {"error": "internal error"}
