"""
Unit Tests for VANA Review Orchestrator (Lifecycle & Parser)
============================================================
Task ID: T-GOV-F01
Assignee: Ansh Gupta
"""

import pytest
from task_selector.review_orchestrator import (
    VanaReviewOrchestrator,
    ReviewStage,
    DecisionState,
    ReviewPacketContract,
    CandidateReviewRecord
)
from evaluation_engine.rule_engine import VanaEvaluationRequest


@pytest.mark.unit
class TestVanaReviewOrchestrator:
    """Test suite for VanaReviewOrchestrator and Parikshak Phase 1 parser."""

    def test_parse_valid_review_packet(self, review_orchestrator, valid_review_packet_markdown):
        """Verify valid markdown correctly extracts all 4 sections and fenced JSON block."""
        result = review_orchestrator.parse_review_packet_markdown(valid_review_packet_markdown)
        assert result["valid"] is True
        assert "ENTRY POINT" in result["sections"]
        assert "CORE FLOW" in result["sections"]
        assert "LIVE FLOW" in result["sections"]
        assert "OUTPUT SAMPLE" in result["sections"]
        data = result["output_sample_data"]
        assert data["evaluation_result"] == "PASS"
        assert data["trace_id"] == "trace-parikshak-proof-tgovf01"

    def test_parse_missing_section(self, review_orchestrator):
        """Verify parser catches missing required section."""
        bad_md = """## ENTRY POINT
api/production.py is the primary entry point.
## CORE FLOW
Step 1 -> Step 2 -> Step 3.
## LIVE FLOW
POST to /api/v1/evaluate.
"""  # Missing OUTPUT SAMPLE
        result = review_orchestrator.parse_review_packet_markdown(bad_md)
        assert result["valid"] is False
        assert "Missing required sections" in result["error"]
        assert "OUTPUT SAMPLE" in result["missing_sections"]

    def test_parse_sections_out_of_order(self, review_orchestrator):
        """Verify parser catches sections in non-canonical order."""
        bad_order_md = """## CORE FLOW
Step 1 -> Step 2 -> Step 3.
## ENTRY POINT
api/production.py is the primary entry point.
## LIVE FLOW
POST to /api/v1/evaluate.
## OUTPUT SAMPLE
```json
{"evaluation_result": "PASS", "failure_type": null, "trace_id": "t1"}
```
"""
        result = review_orchestrator.parse_review_packet_markdown(bad_order_md)
        assert result["valid"] is False
        assert "Sections out of order" in result["error"]

    def test_parse_missing_json_block(self, review_orchestrator):
        """Verify parser catches absence of fenced JSON code block in OUTPUT SAMPLE."""
        no_json_md = """## ENTRY POINT
api/production.py is the main file.
## CORE FLOW
Pipeline flows from Step 1 to Step 5.
## LIVE FLOW
Request is sent via HTTP POST to endpoint.
## OUTPUT SAMPLE
No fenced JSON here, just plain text output!
"""
        result = review_orchestrator.parse_review_packet_markdown(no_json_md)
        assert result["valid"] is False
        assert "missing fenced JSON code block" in result["error"]

    def test_parse_malformed_json_in_output_sample(self, review_orchestrator):
        """Verify parser catches syntactically broken JSON."""
        malformed_json_md = """## ENTRY POINT
api/production.py is the main file.
## CORE FLOW
Pipeline flows from Step 1 to Step 5.
## LIVE FLOW
Request is sent via HTTP POST to endpoint.
## OUTPUT SAMPLE
```json
{ invalid_json: "yes", unquoted }
```
"""
        result = review_orchestrator.parse_review_packet_markdown(malformed_json_md)
        assert result["valid"] is False
        assert "OUTPUT SAMPLE JSON is malformed" in result["error"]

    def test_parse_missing_required_keys_in_json(self, review_orchestrator):
        """Verify parser checks for required keys: evaluation_result, failure_type, trace_id."""
        incomplete_json_md = """## ENTRY POINT
api/production.py is the main file.
## CORE FLOW
Pipeline flows from Step 1 to Step 5.
## LIVE FLOW
Request is sent via HTTP POST to endpoint.
## OUTPUT SAMPLE
```json
{
  "status": "OK",
  "result": "PASS"
}
```
"""
        result = review_orchestrator.parse_review_packet_markdown(incomplete_json_md)
        assert result["valid"] is False
        assert "missing required keys" in result["error"]

    def test_orchestrate_submission_success(self, review_orchestrator, valid_review_packet_markdown):
        """Verify full orchestration completes to VERIFIED_COMPLETE state with PASS decision."""
        record = review_orchestrator.orchestrate_submission(
            task_id="T-GOV-F01",
            candidate_name="Ansh Gupta",
            review_packet_text=valid_review_packet_markdown
        )
        assert isinstance(record, CandidateReviewRecord)
        assert record.stage == ReviewStage.VERIFIED_COMPLETE
        assert record.decision == DecisionState.PASS
        assert record.score == 100.0
        assert record.failure_type is None
        assert record.pac == {"code": 1, "architecture": 1, "proof": 1}
        assert record.rubric == {"has_alignment": 1, "has_effort": 1, "has_code": 1}
        assert len(record.audit_trail) >= 3
        assert record.state_hash is not None

    def test_orchestrate_submission_packet_failure(self, review_orchestrator):
        """Verify invalid review packet yields FAILED stage, score=16, failure_type='schema_violation'."""
        record = review_orchestrator.orchestrate_submission(
            task_id="T-GOV-F01",
            candidate_name="Ansh Gupta",
            review_packet_text="Incomplete packet without any headers"
        )
        assert record.stage == ReviewStage.FAILED
        assert record.decision == DecisionState.FAIL
        assert record.score == 16.0
        assert record.failure_type == "schema_violation"

    def test_orchestrate_submission_rule_failure(self, review_orchestrator, valid_review_packet_markdown):
        """Verify failing evaluation request results in REMEDIATION_REQUIRED decision."""
        bad_req = VanaEvaluationRequest(
            actor="VANA",
            role="APPROVED_CONSUMER",
            dataset_id="DS-UNKNOWN",  # Will fail governance check
            action="READ",
            purpose="DISTRICT_CANOPY_ANALYSIS"
        )
        record = review_orchestrator.orchestrate_submission(
            task_id="T-GOV-F01",
            candidate_name="Ansh Gupta",
            review_packet_text=valid_review_packet_markdown,
            evaluation_request=bad_req
        )
        assert record.stage == ReviewStage.FAILED
        assert record.decision == DecisionState.REMEDIATION_REQUIRED
        assert record.failure_type == "incorrect_logic"

    def test_review_packet_contract_model(self):
        """Verify ReviewPacketContract model validation."""
        contract = ReviewPacketContract(
            entry_point="api/production.py is the primary entrypoint",
            core_flow="Data enters pipeline -> undergoes schema verification -> governance check -> response",
            live_flow="Requests sent via POST /api/v1/evaluate to obtain deterministic hash",
            output_sample={"evaluation_result": "PASS", "failure_type": None, "trace_id": "tid-1"},
            self_audit_score=100.0
        )
        assert contract.validate_keys() is True

        bad_contract = ReviewPacketContract(
            entry_point="api/production.py is the primary entrypoint",
            core_flow="Data enters pipeline -> undergoes schema verification -> governance check -> response",
            live_flow="Requests sent via POST /api/v1/evaluate to obtain deterministic hash",
            output_sample={"some_other_key": 123},
            self_audit_score=50.0
        )
        assert bad_contract.validate_keys() is False
