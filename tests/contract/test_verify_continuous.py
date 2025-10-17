from pathlib import Path
import yaml


def test_openapi_supports_continuous_and_score():
    p = Path("specs/001-claim-verification-api/contracts/openapi.yaml").resolve()
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    j = data["components"]["schemas"]["Judgment"]
    # Ensure kind includes continuous and score range defined
    assert "continuous" in j["properties"]["kind"]["enum"]
    score = j["properties"]["score"]
    assert score["minimum"] == 0 and score["maximum"] == 1

