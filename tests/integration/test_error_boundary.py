"""
Integration Tests for Complete Error Boundary Protection & Schema Strictness
============================================================================
Task ID: T-GOV-F01
Assignee: Ansh Gupta

Fulfills Strict Acceptance Criteria:
- Complete error boundary protection: zero unhandled 500 exceptions on malformed inputs
- All API routes validate inbound request schemas with strict Pydantic models
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestErrorBoundaryProtection:
    """Test suite asserting zero unhandled 500 exceptions on malformed inputs and boundary violations."""

    def test_evaluate_malformed_json_syntax(self, client):
        """Verify broken raw JSON syntax returns 422 validation error, zero unhandled 500."""
        resp = client.post(
            "/api/v1/evaluate",
            content=b"{malformed_json_missing_quotes: true",
            headers={"Content-Type": "application/json"}
        )
        assert resp.status_code == 422
        data = resp.json()
        assert data["success"] is False
        assert data["error"] == "ValidationError"
        assert "trace_id" in data
        assert "validation_errors" in data

    def test_evaluate_missing_required_fields(self, client):
        """Verify payload missing required fields returns 422 with specific error details."""
        resp = client.post("/api/v1/evaluate", json={"actor": "VANA"})
        assert resp.status_code == 422
        data = resp.json()
        assert data["success"] is False
        assert data["error"] == "ValidationError"
        fields = [e["field"] for e in data["validation_errors"]]
        assert any("role" in f for f in fields)
        assert any("dataset_id" in f for f in fields)

    def test_evaluate_invalid_field_types(self, client):
        """Verify invalid field types (e.g., action is an integer) return 422, not 500."""
        resp = client.post("/api/v1/evaluate", json={
            "actor": "VANA",
            "role": "APPROVED_CONSUMER",
            "dataset_id": "DS-FSI-ISFR-2023-FOREST-COVER",
            "action": 12345,  # Must be string matching pattern
            "purpose": "DISTRICT_CANOPY_ANALYSIS"
        })
        assert resp.status_code == 422
        data = resp.json()
        assert data["error"] == "ValidationError"

    def test_evaluate_disallowed_action_pattern(self, client):
        """Verify unpermitted action regex string returns 422."""
        resp = client.post("/api/v1/evaluate", json={
            "actor": "VANA",
            "role": "APPROVED_CONSUMER",
            "dataset_id": "DS-FSI-ISFR-2023-FOREST-COVER",
            "action": "DROP_TABLE",  # Disallowed regex pattern
            "purpose": "DISTRICT_CANOPY_ANALYSIS"
        })
        assert resp.status_code == 422
        data = resp.json()
        assert data["error"] == "ValidationError"

    def test_review_orchestrate_empty_body(self, client):
        """Verify empty body to review orchestrator returns 422."""
        resp = client.post("/api/v1/review/orchestrate", json={})
        assert resp.status_code == 422
        data = resp.json()
        assert data["error"] == "ValidationError"

    def test_auth_login_malformed_inputs(self, client):
        """Verify invalid email / password types return 422."""
        resp = client.post("/api/v1/auth/login", json={"email": ""})
        assert resp.status_code == 422
        data = resp.json()
        assert data["error"] == "ValidationError"

    def test_carbon_thane_creek_negative_parameters(self, client):
        """Verify query parameters violating min bounds return 422, not 500."""
        resp = client.get("/api/v1/carbon/thane-creek?area_ha=-50.0")
        assert resp.status_code == 422
        data = resp.json()
        assert data["error"] == "ValidationError"

    def test_determinism_endpoint_out_of_range(self, client):
        """Verify determinism runs query exceeding max (100) returns 422, not 500."""
        resp = client.get("/api/v1/evaluate/determinism?runs=500")
        assert resp.status_code == 422
        data = resp.json()
        assert data["error"] == "ValidationError"

    def test_vana_execute_missing_observation_id(self, client, admin_token):
        """Verify /vana/execute with missing required observation_id returns 422, not 500."""
        resp = client.post(
            "/vana/execute",
            json={"capability": "environmental_observation"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 422
        data = resp.json()
        assert data["error"] == "ValidationError"

    def test_non_existent_route_404(self, client):
        """Verify non-existent routes return structured 404, not unhandled crash."""
        resp = client.get("/non_existent_route_random_123")
        assert resp.status_code == 404
