"""
Unit Tests for VANA Rule Engine (Deterministic Governance)
==========================================================
Task ID: T-GOV-F01
Assignee: Ansh Gupta
"""

import pytest
from pydantic import ValidationError

from evaluation_engine.rule_engine import (
    VanaRuleEngine,
    VanaEvaluationRequest,
    VanaEvaluationResponse,
    RuleEvaluationResult,
    EvaluationRubric
)


@pytest.mark.unit
class TestVanaRuleEngine:
    """Test suite for VanaRuleEngine 5-gate pipeline and determinism."""

    def test_evaluate_valid_request_pass(self, rule_engine, valid_eval_request):
        """Verify standard canonical request passes all 5 gates with 100% score."""
        resp = rule_engine.evaluate(valid_eval_request)
        assert isinstance(resp, VanaEvaluationResponse)
        assert resp.evaluation_result == "PASS"
        assert resp.failure_type is None
        assert resp.score == 100.0
        assert resp.pac == {"code": 1, "architecture": 1, "proof": 1}
        assert resp.rubric == {"has_alignment": 1, "has_effort": 1, "has_code": 1}
        assert len(resp.rule_results) == 5
        assert all(r.passed for r in resp.rule_results)
        assert resp.state_hash is not None
        assert len(resp.state_hash) == 64

    def test_gate1_schema_strictness_missing_fields(self, rule_engine):
        """Gate 1: Verify schema validation catches missing or empty fields."""
        with pytest.raises(ValidationError):
            VanaEvaluationRequest(
                actor="",  # Too short
                role="APPROVED_CONSUMER",
                dataset_id="DS-FSI-ISFR-2023-FOREST-COVER",
                action="READ",
                purpose="DISTRICT_CANOPY_ANALYSIS"
            )

    def test_gate1_action_pattern_validation(self):
        """Gate 1: Action must match strict pattern."""
        with pytest.raises(ValidationError):
            VanaEvaluationRequest(
                actor="VANA",
                role="APPROVED_CONSUMER",
                dataset_id="DS-FSI-ISFR-2023-FOREST-COVER",
                action="INVALID_ACTION",  # invalid
                purpose="DISTRICT_CANOPY_ANALYSIS"
            )

    def test_gate2_completeness_trivial_purpose(self, rule_engine):
        """Gate 2: Verify trivial or short purpose triggers incomplete failure."""
        req = VanaEvaluationRequest(
            actor="VANA",
            role="APPROVED_CONSUMER",
            dataset_id="DS-FSI-ISFR-2023-FOREST-COVER",
            action="READ",
            purpose="test",  # Trivial
            environment="production"
        )
        resp = rule_engine.evaluate(req)
        assert resp.evaluation_result == "FAIL"
        assert resp.failure_type == "incomplete"
        r2 = next(r for r in resp.rule_results if r.rule_id == "R-COMP-02")
        assert not r2.passed
        assert r2.score == 20.0

    def test_gate3_scientific_doctrine_silent_mixing(self, rule_engine):
        """Gate 3: Verify doctrine violation when measured & estimated are blended without variance."""
        req = VanaEvaluationRequest(
            actor="VANA",
            role="APPROVED_CONSUMER",
            dataset_id="DS-FSI-ISFR-2023-FOREST-COVER",
            action="READ",
            purpose="DISTRICT_CANOPY_ANALYSIS",
            carbon_payload={
                "measured_agb": 84.83,
                "estimated_agb": 111.31,
                "silently_mixed": True
            }
        )
        resp = rule_engine.evaluate(req)
        assert resp.evaluation_result == "FAIL"
        assert resp.failure_type == "incorrect_logic"
        r3 = next(r for r in resp.rule_results if r.rule_id == "R-SCI-03")
        assert not r3.passed
        assert "silently blended" in r3.observation

    def test_gate3_scientific_doctrine_blended_without_variance(self, rule_engine):
        """Gate 3: Verify violation when blended_without_variance is set to True."""
        req = VanaEvaluationRequest(
            actor="VANA",
            role="APPROVED_CONSUMER",
            dataset_id="DS-FSI-ISFR-2023-FOREST-COVER",
            action="READ",
            purpose="DISTRICT_CANOPY_ANALYSIS",
            carbon_payload={
                "measured_agb": 84.83,
                "estimated_agb": 111.31,
                "blended_without_variance": True
            }
        )
        resp = rule_engine.evaluate(req)
        assert resp.evaluation_result == "FAIL"
        assert resp.failure_type == "incorrect_logic"

    def test_gate4_governance_unregistered_dataset(self, rule_engine):
        """Gate 4: Verify unregistered dataset is rejected by 6-tuple governance."""
        req = VanaEvaluationRequest(
            actor="VANA",
            role="APPROVED_CONSUMER",
            dataset_id="DS-UNKNOWN-UNGOVERNED-DATASET",
            action="READ",
            purpose="DISTRICT_CANOPY_ANALYSIS"
        )
        resp = rule_engine.evaluate(req)
        assert resp.evaluation_result == "FAIL"
        assert resp.failure_type == "incorrect_logic"
        r4 = next(r for r in resp.rule_results if r.rule_id == "R-GOV-04")
        assert not r4.passed
        assert "not registered" in r4.observation

    def test_gate4_governance_unauthorized_role(self, rule_engine):
        """Gate 4: Role not in allowed_roles list for dataset."""
        req = VanaEvaluationRequest(
            actor="VANA",
            role="UNAUTHORIZED_GUEST",
            dataset_id="DS-FSI-ISFR-2023-FOREST-COVER",
            action="READ",
            purpose="DISTRICT_CANOPY_ANALYSIS"
        )
        resp = rule_engine.evaluate(req)
        assert resp.evaluation_result == "FAIL"
        r4 = next(r for r in resp.rule_results if r.rule_id == "R-GOV-04")
        assert not r4.passed
        assert "not authorized" in r4.observation

    def test_gate4_governance_unpermitted_action(self, rule_engine):
        """Gate 4: Action not in allowed_actions list."""
        req = VanaEvaluationRequest(
            actor="VANA",
            role="APPROVED_CONSUMER",
            dataset_id="DS-THANECREEK-2023-BIOMASS",
            action="WRITE",  # Only READ is allowed
            purpose="BLUE_CARBON_SEQUESTRATION"
        )
        resp = rule_engine.evaluate(req)
        assert resp.evaluation_result == "FAIL"
        r4 = next(r for r in resp.rule_results if r.rule_id == "R-GOV-04")
        assert not r4.passed
        assert "Action 'WRITE' is not permitted" in r4.observation

    def test_gate4_governance_unapproved_purpose(self, rule_engine):
        """Gate 4: Purpose not in allowed_purposes list."""
        req = VanaEvaluationRequest(
            actor="VANA",
            role="APPROVED_CONSUMER",
            dataset_id="DS-FSI-ISFR-2023-FOREST-COVER",
            action="READ",
            purpose="COMMERCIAL_AD_TARGETING"  # Not approved
        )
        resp = rule_engine.evaluate(req)
        assert resp.evaluation_result == "FAIL"
        r4 = next(r for r in resp.rule_results if r.rule_id == "R-GOV-04")
        assert not r4.passed
        assert "not pre-approved" in r4.observation

    def test_gate5_synthetic_quarantine_canonical_dataset(self, rule_engine):
        """Gate 5: Synthetic data attempting to write/read as CANONICAL must be quarantined."""
        req = VanaEvaluationRequest(
            actor="VANA",
            role="APPROVED_CONSUMER",
            dataset_id="DS-FSI-ISFR-2023-FOREST-COVER",
            action="READ",
            purpose="DISTRICT_CANOPY_ANALYSIS",
            is_synthetic=True  # Quarantine violation
        )
        resp = rule_engine.evaluate(req)
        assert resp.evaluation_result == "FAIL"
        assert resp.failure_type == "quarantine_violation"
        r5 = next(r for r in resp.rule_results if r.rule_id == "R-QUAR-05")
        assert not r5.passed
        assert "Quarantine trigger" in r5.observation

    @pytest.mark.determinism
    def test_50_consecutive_runs_deterministic_hashes(self, rule_engine):
        """Quality Gate: 50 consecutive runs must produce identical SHA-256 state hashes."""
        audit = rule_engine.compute_deterministic_state_hash(runs=50)
        assert audit["runs"] == 50
        assert audit["unique_hashes_count"] == 1
        assert audit["is_deterministic"] is True
        assert audit["all_hashes_identical"] is True
        assert audit["sample_hash"] is not None
        assert len(audit["sample_hash"]) == 64

    def test_evaluation_rubric_defaults(self):
        """Verify rubric defaults are instantiated with full compliance."""
        rubric = EvaluationRubric()
        assert rubric.code_present is True
        assert rubric.proof_present is True
        assert rubric.arch_present is True
        assert rubric.composite_score == 100.0
        assert rubric.evaluation_result == "PASS"
