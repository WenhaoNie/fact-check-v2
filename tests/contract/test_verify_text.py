from pathlib import Path
import yaml


def test_openapi_contract_has_verify_post():
    openapi_path = Path("specs/001-claim-verification-api/contracts/openapi.yaml").resolve()
    assert openapi_path.exists(), f"OpenAPI file not found: {openapi_path}"

    data = yaml.safe_load(openapi_path.read_text(encoding="utf-8"))
    assert "paths" in data and "/v1/verify" in data["paths"], "Missing /v1/verify path"
    post = data["paths"]["/v1/verify"].get("post")
    assert post, "POST /v1/verify not defined"

    # Verify request schema wiring
    rb = post.get("requestBody", {})
    assert rb.get("required") is True
    content = rb.get("content", {}).get("application/json", {})
    schema_ref = content.get("schema", {}).get("$ref", "")
    assert "#/components/schemas/VerifyRequest" in schema_ref

    # Verify response schema wiring
    resp200 = post.get("responses", {}).get("200", {})
    content200 = resp200.get("content", {}).get("application/json", {})
    resp_ref = content200.get("schema", {}).get("$ref", "")
    assert "#/components/schemas/VerifyResponse" in resp_ref

