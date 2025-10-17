from services.verification_service import verify_claim


def test_continuous_scoring_is_present_and_stable():
    payload = {
        "input": {"type": "text", "claim_text": "A company revenue grew 20% YoY", "locale": "en"},
        "output": {"kind": "continuous"},
    }
    scores = []
    bins = []
    for _ in range(3):
        res = verify_claim(payload)
        j = res["judgment"]
        assert j.get("score") is not None
        scores.append(float(j["score"]))
        bins.append(j.get("binary"))
    # Scores should be equal or vary minimally due to deterministic heuristic
    assert max(scores) - min(scores) <= 0.01
    # Binary should be in allowed set
    for b in bins:
        assert b in {"yes", "no", "unknown", None}

