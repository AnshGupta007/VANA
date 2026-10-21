"""
Unit Tests for VANA Security Middleware & RBAC
==============================================
Task ID: T-GOV-F01
Assignee: Ansh Gupta
"""

import pytest
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.testclient import TestClient

from security.middleware import (
    ErrorBoundaryMiddleware,
    UserRole,
    require_role,
    register_used_token,
    validate_request_signature
)
from vana_auth import create_access_token


@pytest.mark.unit
class TestSecurityMiddleware:
    """Test suite for error boundary, replay defense, and RBAC."""

    def test_token_replay_protection(self):
        """Verify token replay protection flags repeated token presentations."""
        token_a = "sample-token-random-abc-12345"
        token_b = "sample-token-random-def-67890"

        assert register_used_token(token_a) is True
        assert register_used_token(token_a) is False  # Replay detected
        assert register_used_token(token_b) is True

    def test_validate_request_signature(self):
        """Verify HMAC request signature validation."""
        import hashlib
        payload = '{"amount": 100}'
        secret = "vana-secret-key-99"
        expected = hashlib.sha256(f"{payload}:{secret}".encode()).hexdigest()

        assert validate_request_signature(payload, expected, secret) is True
        assert validate_request_signature(payload, "wrong-signature", secret) is False

    def test_error_boundary_middleware_catches_unhandled_crash(self):
        """Verify middleware catches unhandled exceptions and returns structured 500 JSON envelope."""
        test_app = FastAPI()
        test_app.add_middleware(ErrorBoundaryMiddleware)

        @test_app.get("/crash")
        def crash_route():
            raise ZeroDivisionError("Simulated unhandled system crash!")

        @test_app.get("/normal")
        def normal_route():
            return {"status": "ok"}

        client = TestClient(test_app, raise_server_exceptions=False)

        # Test normal response
        res_normal = client.get("/normal")
        assert res_normal.status_code == 200
        assert "X-Trace-Id" in res_normal.headers
        assert "X-Response-Time" in res_normal.headers

        # Test crashed response caught by boundary
        res_crash = client.get("/crash")
        assert res_crash.status_code == 500
        data = res_crash.json()
        assert data["success"] is False
        assert data["error"] == "InternalServerError"
        assert "trace_id" in data
        assert data["path"] == "/crash"
        assert "ZeroDivisionError" not in data["detail"]  # Prevents internal traceback leakage

    def test_require_role_api_key_bypass(self):
        """Verify master API key bypasses JWT check and grants admin/PLATFORM_ADMIN authority."""
        test_app = FastAPI()

        @test_app.get("/admin-only")
        def admin_route(user=Depends(require_role([UserRole.ADMIN]))):
            return {"user": user}

        client = TestClient(test_app)
        res = client.get("/admin-only", headers={"X-API-Key": "vana_test_key_master"})
        assert res.status_code == 200
        assert res.json()["user"]["role"] == "admin"
        assert res.json()["user"]["governance_role"] == "PLATFORM_ADMIN"

    def test_require_role_missing_auth(self):
        """Verify missing authorization returns 401."""
        test_app = FastAPI()

        @test_app.get("/protected")
        def protected_route(user=Depends(require_role([UserRole.PARTICIPANT]))):
            return {"user": user}

        client = TestClient(test_app)
        res = client.get("/protected")
        assert res.status_code == 401
        assert "Authentication required" in res.json()["detail"]

    def test_require_role_forbidden_access(self, participant_token):
        """Verify participant role accessing admin-only endpoint is rejected with 403."""
        test_app = FastAPI()

        @test_app.get("/admin-strictly")
        def admin_strictly_route(user=Depends(require_role([UserRole.ADMIN]))):
            return {"user": user}

        client = TestClient(test_app)
        res = client.get("/admin-strictly", headers={"Authorization": f"Bearer {participant_token}"})
        assert res.status_code == 403
        assert "Access Denied" in res.json()["detail"]

    def test_require_role_authorized_access(self, admin_token):
        """Verify admin token successfully accesses admin-gated endpoint."""
        test_app = FastAPI()

        @test_app.get("/admin-strictly")
        def admin_strictly_route(user=Depends(require_role([UserRole.ADMIN]))):
            return {"user": user}

        client = TestClient(test_app)
        res = client.get("/admin-strictly", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        assert res.json()["user"]["role"] == "admin"
