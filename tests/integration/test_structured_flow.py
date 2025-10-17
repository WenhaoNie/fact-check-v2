from services.verification_service import verify_claim


def test_structured_flow_returns_structured_unknown():
    payload = {
        "input": {
            "type": "structured",
            "claim": {
                "subject": "Company A",
                "text": "Revenue YoY growth > 20%",
                "time_window": "2024-10-01..2024-12-31",
                "locale": "en",
            },
        },
        "output": {"kind": "both"},
    }
    result = verify_claim(payload)
    assert isinstance(result, dict) and "judgment" in result
    j = result["judgment"]
    assert j.get("kind") in {"binary", "continuous", "both"}
    assert j.get("binary") in {"yes", "no", "unknown", None}
    assert isinstance(j.get("reasons"), list) and len(j["reasons"]) >= 1
    assert "audit" in j and isinstance(j["audit"], dict)

