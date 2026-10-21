"""
Integration Tests for VANA / FIN Production API
================================================
Task ID: T-GOV-F01
Assignee: Ansh Gupta
"""

import uuid
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestApiProduction:
    """End-to-end integration test suite covering production API endpoints."""

    def test_health_check(self, client):
        """Verify health check returns healthy status and all 8 active subsystems."""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "VANA / FIN Environmental Intelligence Platform"
        assert "subsystems" in data
        assert data["subsystems"]["masterdb"] == "ONLINE"
        assert data["subsystems"]["error_boundary_middleware"] == "ACTIVE"
        assert data["subsystems"]["deterministic_rule_engine"] == "ONLINE"

    def test_evaluate_endpoint_pass(self, client, valid_eval_request):
        """Verify /api/v1/evaluate processes compliant request and returns 200 OK."""
        resp = client.post("/api/v1/evaluate", json=valid_eval_request.model_dump())
        assert resp.status_code == 200
        data = resp.json()
        assert data["evaluation_result"] == "PASS"
        assert data["failure_type"] is None
        assert data["score"] == 100.0
        assert "state_hash" in data
        assert len(data["state_hash"]) == 64

    def test_evaluate_determinism_endpoint(self, client):
        """Verify /api/v1/evaluate/determinism confirms 50 identical runs."""
        resp = client.get("/api/v1/evaluate/determinism?runs=50")
        assert resp.status_code == 200
        data = resp.json()
        assert data["runs"] == 50
        assert data["unique_hashes_count"] == 1
        assert data["is_deterministic"] is True
        assert data["all_hashes_identical"] is True

    def test_orchestrate_review_endpoint(self, client, valid_review_packet_markdown):
        """Verify /api/v1/review/orchestrate parses packet and returns VERIFIED_COMPLETE."""
        payload = {
            "task_id": "T-GOV-F01",
            "candidate_name": "Ansh Gupta",
            "review_packet_text": valid_review_packet_markdown
        }
        resp = client.post("/api/v1/review/orchestrate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["stage"] == "VERIFIED_COMPLETE"
        assert data["decision"] == "PASS"
        assert data["score"] == 100.0

    def test_auth_login_success(self, client):
        """Verify login with seed admin account succeeds."""
        resp = client.post("/api/v1/auth/login", json={
            "email": "admin@vana.bhiv",
            "password": "Admin@123"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "access_token" in data
        assert data["user"]["email"] == "admin@vana.bhiv"
        assert data["user"]["role"] == "admin"

    def test_auth_login_invalid_credentials(self, client):
        """Verify invalid credentials return 401."""
        resp = client.post("/api/v1/auth/login", json={
            "email": "admin@vana.bhiv",
            "password": "WrongPassword999!"
        })
        assert resp.status_code == 401
        data = resp.json()
        assert data["success"] is False

    def test_auth_register_and_profile(self, client):
        """Verify registration and profile retrieval."""
        random_email = f"test_{uuid.uuid4().hex[:6]}@vana.bhiv"
        reg_resp = client.post("/api/v1/auth/register", json={
            "name": "Integration Tester",
            "email": random_email,
            "password": "SecurePassword@123",
            "role": "participant"
        })
        assert reg_resp.status_code == 200
        token = reg_resp.json()["access_token"]

        # Fetch profile
        me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_resp.status_code == 200
        assert me_resp.json()["user"]["email"] == random_email

    def test_auth_roles_endpoint(self, client):
        """Verify /api/v1/auth/roles returns RBAC specification and test accounts."""
        resp = client.get("/api/v1/auth/roles")
        assert resp.status_code == 200
        data = resp.json()
        assert "frontend_roles" in data
        assert "governance_roles" in data
        assert "role_mapping" in data

    def test_carbon_endpoints(self, client):
        """Verify carbon summary, Maharashtra, and Thane Creek calculations."""
        # Summary
        resp_sum = client.get("/api/v1/carbon/summary")
        assert resp_sum.status_code == 200
        assert "forest_carbon_summary" in resp_sum.json()
        assert "blue_carbon_summary" in resp_sum.json()

        # Maharashtra forest
        resp_mh = client.get("/api/v1/carbon/maharashtra")
        assert resp_mh.status_code == 200
        assert "carbon_metrics" in resp_mh.json()

        # Thane Creek blue carbon
        resp_tc = client.get("/api/v1/carbon/thane-creek?area_ha=896.0&measured_agb=84.83&estimated_agb=111.31")
        assert resp_tc.status_code == 200
        assert "total_ecosystem_reservoir_summary" in resp_tc.json()

    def test_spatial_endpoints(self, client):
        """Verify spatial layers, geojson, and unified envelope."""
        resp_layers = client.get("/api/v1/spatial/layers")
        assert resp_layers.status_code == 200
        assert resp_layers.json()["status"] == "SUCCESS"

        resp_geojson = client.get("/api/v1/spatial/geojson/thane_creek_sanctuary")
        assert resp_geojson.status_code == 200
        assert resp_geojson.json()["type"] in ("Feature", "FeatureCollection")

        # 404 for unknown layer
        resp_404 = client.get("/api/v1/spatial/geojson/non_existent_layer")
        assert resp_404.status_code == 404

        resp_envelope = client.get("/api/v1/spatial/envelope")
        assert resp_envelope.status_code == 200

    def test_masterdb_real_observations(self, client):
        """Verify MasterDB real observations endpoint."""
        resp = client.get("/api/v1/observations/real")
        assert resp.status_code == 200
        data = resp.json()
        assert "count" in data
        assert "observations" in data
        assert data["count"] > 0

    def test_masterdb_forest_records(self, client):
        """Verify official ISFR forest cover records."""
        resp = client.get("/api/v1/official/forest-cover/records")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] > 0

    def test_weather_endpoint(self, client):
        """Verify Open-Meteo Thane Creek coastal station weather telemetry."""
        resp = client.get("/api/v1/weather/thane-creek")
        assert resp.status_code == 200
        data = resp.json()
        assert "metrics" in data

    def test_governance_datasets(self, client):
        """Verify governed datasets catalog."""
        resp = client.get("/api/v1/governance/datasets")
        assert resp.status_code == 200
        assert resp.json()["count"] >= 3

    def test_governance_audit_log(self, client, admin_token):
        """Verify governance audit log with admin authority."""
        resp = client.get("/api/v1/governance/audit-log", headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        assert "audit_trail" in resp.json()

    def test_vana_execute_success(self, client, admin_token):
        """Verify TANTRA execution gate succeeds with valid payload and admin token."""
        payload = {
            "observation_id": "OBS-THANECREEK-BIOMASS-01",
            "capability": "environmental_observation",
            "ruling": "PROCEED",
            "action_eligibility": True
        }
        resp = client.post("/vana/execute", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "EXECUTED"
        assert data["decision"] == "ALLOWED"
        assert "evidence_hash" in data

    def test_vana_execute_refused_unauthorized_product(self, client, admin_token):
        """Verify TANTRA execution gate refuses unauthorized product."""
        payload = {
            "observation_id": "OBS-THANECREEK-BIOMASS-01",
            "product_id": "ROGUE_UNAUTHORIZED_SYSTEM"
        }
        resp = client.post("/vana/execute", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 403
        data = resp.json()
        assert data["decision"] == "REFUSED"
        assert data["gate_failed"] == "AUTHORITY"

    def test_vana_execute_governed_abstention(self, client, admin_token):
        """Verify TANTRA execution enforces safe governed abstention when ruling is ABSTAIN."""
        payload = {
            "observation_id": "OBS-THANECREEK-BIOMASS-01",
            "ruling": "ABSTAIN",
            "abstention_required": True
        }
        resp = client.post("/vana/execute", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["decision"] == "GOVERNED_ABSTENTION"
        assert data["gate_failed"] == "SEMANTIC"
