import os
import sys
from pathlib import Path


# Ensure 'src' is importable when running tests from repo root
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Default environment tweaks for tests
os.environ.setdefault("SEARCH_PROVIDER", "brave")
os.environ.setdefault("BRAVE_KEY_FILE", "/keys/BRAVE_API_KEY")

