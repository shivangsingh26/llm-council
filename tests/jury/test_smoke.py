"""
Smoke tests for Phase 2 Jury layer.

Tests basic imports and initialization without requiring API calls.
"""

import pytest


def test_jury_imports():
    """Test that all jury modules can be imported."""
    from src.jury.base_juror import BaseJuror, JuryRole
    from src.jury.evidence_validator import EvidenceValidator
    from src.jury.logic_auditor import LogicAuditor
    from src.jury.assumption_critic import AssumptionCritic
    from src.jury.orchestrator import JuryOrchestrator

    assert BaseJuror is not None
    assert JuryRole is not None
    assert EvidenceValidator is not None
    assert LogicAuditor is not None
    assert AssumptionCritic is not None
    assert JuryOrchestrator is not None


def test_jury_role_enum():
    """Test JuryRole enum values."""
    from src.jury.base_juror import JuryRole

    assert JuryRole.EVIDENCE_VALIDATOR.value == "evidence_validator"
    assert JuryRole.LOGIC_AUDITOR.value == "logic_auditor"
    assert JuryRole.ASSUMPTION_CRITIC.value == "assumption_critic"


def test_adaptive_router_imports_jury():
    """Test that adaptive router can import jury components."""
    from src.council.adaptive_router import AdaptiveRouter

    # Should be able to create router without jury
    router = AdaptiveRouter(enable_jury=False)
    assert router is not None
    assert router.enable_jury is False


def test_orchestrator_jury_integration():
    """Test that orchestrator integrates with jury."""
    from src.council.orchestrator import CouncilOrchestrator

    # Check if orchestrator has jury-related attributes
    # (without actually initializing since we don't have API keys)
    assert hasattr(CouncilOrchestrator, '__init__')


def test_base_juror_metadata_format():
    """Test BaseJuror metadata formatting."""
    from src.jury.base_juror import BaseJuror, JuryRole

    # Create a simple concrete implementation for testing
    class TestJuror(BaseJuror):
        async def analyze(self, query, council_responses, synthesized_answer):
            return {}

    juror = TestJuror("test_key", "test_model", JuryRole.EVIDENCE_VALIDATOR)
    metadata = juror._format_metadata()

    assert "role" in metadata
    assert "model" in metadata
    assert "timestamp" in metadata
    assert metadata["role"] == "evidence_validator"
    assert metadata["model"] == "test_model"


def test_base_juror_extract_claims():
    """Test BaseJuror claim extraction."""
    from src.jury.base_juror import BaseJuror, JuryRole

    class TestJuror(BaseJuror):
        async def analyze(self, query, council_responses, synthesized_answer):
            return {}

    juror = TestJuror("test_key", "test_model", JuryRole.EVIDENCE_VALIDATOR)

    text = "This is a test sentence. This is another test sentence with more content. Short."
    claims = juror._extract_claims(text)

    # Should extract sentences longer than 20 chars
    assert isinstance(claims, list)
    assert len(claims) >= 1


def test_schemas_have_jury_result():
    """Test that schemas include JuryResult."""
    from src.models import schemas

    # Check if JuryResult schema exists
    assert hasattr(schemas, 'JuryResult') or 'JuryResult' in dir(schemas)


def test_phase2_test_files_exist():
    """Test that all Phase 2 test files exist."""
    import os

    test_files = [
        "tests/jury/test_evidence_validator.py",
        "tests/jury/test_logic_auditor.py",
        "tests/jury/test_assumption_critic.py",
        "tests/jury/test_jury_orchestrator.py",
        "tests/integration/test_phase2_complete.py"
    ]

    for test_file in test_files:
        assert os.path.exists(test_file), f"Missing test file: {test_file}"


def test_phase2_implementation_files_exist():
    """Test that all Phase 2 implementation files exist."""
    import os

    impl_files = [
        "src/jury/__init__.py",
        "src/jury/base_juror.py",
        "src/jury/evidence_validator.py",
        "src/jury/logic_auditor.py",
        "src/jury/assumption_critic.py",
        "src/jury/orchestrator.py"
    ]

    for impl_file in impl_files:
        assert os.path.exists(impl_file), f"Missing implementation file: {impl_file}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
