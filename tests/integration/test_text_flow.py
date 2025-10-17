import pytest


def test_natural_language_flow_contract_first():
    # Contract-driven: expect a service entrypoint to exist later.
    with pytest.raises(Exception):
        # Import should fail until VerificationService and pipelines are implemented.
        from services.verification_service import verify_claim  # type: ignore  # noqa: F401

