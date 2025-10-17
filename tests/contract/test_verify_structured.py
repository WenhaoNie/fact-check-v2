from pathlib import Path
import yaml


def test_openapi_contract_supports_structured_input():
    openapi_path = Path("specs/001-claim-verification-api/contracts/openapi.yaml").resolve()
    assert openapi_path.exists(), f"OpenAPI file not found: {openapi_path}"

    data = yaml.safe_load(openapi_path.read_text(encoding="utf-8"))
    ci = data["components"]["schemas"]["ClaimInput"]
    assert "enum" in ci["properties"]["type"]
    assert "structured" in ci["properties"]["type"]["enum"]
    # Ensure Claim schema exists
    assert "Claim" in data["components"]["schemas"]

