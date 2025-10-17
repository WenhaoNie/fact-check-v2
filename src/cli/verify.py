from __future__ import annotations

import json
import sys

from services.verification_service import verify_claim


def main() -> int:
    data = json.load(sys.stdin)
    result = verify_claim(data)
    json.dump(result, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
