from services.verification_service import verify_claim


def test_natural_language_flow_returns_structured_unknown():
    payload = {
        "input": {"type": "text", "claim_text": "公司A在2024年Q4营收同比增长超20%", "locale": "zh"},
        "output": {"kind": "both"},
    }
    result = verify_claim(payload)
    assert isinstance(result, dict) and "judgment" in result
    j = result["judgment"]
    # Basic shape assertions
    assert j.get("kind") in {"binary", "continuous", "both"}
    assert j.get("binary") in {"yes", "no", "unknown", None}
    assert isinstance(j.get("reasons"), list) and len(j["reasons"]) >= 1
    assert "audit" in j and isinstance(j["audit"], dict)
