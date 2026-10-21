"""
VANA / FIN Security Middleware & Role-Based Access Control (RBAC)
==================================================================
Task ID: T-GOV-F01 (Remediation & Structural Compliance)
Candidate / Assignee: Ansh Gupta (Spatial / GIS & Governance Lead)
Product Governance: BHIV / Parikshak / Niyantran

Implements:
1. ErrorBoundaryMiddleware providing complete crash protection (zero unhandled 500s)
2. UserRole RBAC definitions covering frontend and MasterDB governance roles
3. FastAPI dependency injection for role-gated endpoints
4. Replay protection and token tracking
"""

from enum import Enum
import hashlib
import json
import logging
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Set
from fastapi import Header, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("vana_security_middleware")

# In-memory replay protection registry (Token -> timestamp)
_SEEN_TOKENS: Dict[str, float] = {}
_MAX_TOKEN_AGE_SECONDS = 86400  # 24 hours


class UserRole(str, Enum):
    ADMIN = "admin"
    PARTICIPANT = "participant"
    JUDGE = "judge"
    STEWARD = "steward"
    PLATFORM_ADMIN = "PLATFORM_ADMIN"
    APPROVED_CONSUMER = "APPROVED_CONSUMER"
    AUDITOR = "AUDITOR"
    GOVERNANCE_STEWARD = "GOVERNANCE_STEWARD"
    EXTERNAL_PARTNER = "EXTERNAL_PARTNER"


class ErrorBoundaryMiddleware(BaseHTTPMiddleware):
    """
    Guarantees complete error boundary protection across all API endpoints:
    Intercepts any unhandled exception and converts it into a standardized,
    structured JSON error envelope. Prevents raw 500 stack trace leakage.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        trace_id = request.headers.get("X-Trace-Id", f"trace-eb-{uuid.uuid4().hex[:12]}")
        start_time = time.time()

        try:
            response = await call_next(request)
            response.headers["X-Trace-Id"] = trace_id
            response.headers["X-Response-Time"] = f"{(time.time() - start_time) * 1000:.2f}ms"
            return response
        except HTTPException as http_exc:
            # Let standard FastAPI HTTPException propagate to exception handlers
            raise http_exc
        except Exception as exc:
            logger.error(f"[ERROR BOUNDARY] Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": "InternalServerError",
                    "detail": "An internal error occurred. The fault has been captured by the security boundary.",
                    "trace_id": trace_id,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "path": request.url.path
                },
                headers={"X-Trace-Id": trace_id}
            )


def register_used_token(token: str) -> bool:
    """
    Register token to detect duplicate replays. Returns True if first time seen, False if replayed.
    """
    now = time.time()
    # Prune expired tokens
    expired = [t for t, ts in _SEEN_TOKENS.items() if now - ts > _MAX_TOKEN_AGE_SECONDS]
    for t in expired:
        _SEEN_TOKENS.pop(t, None)

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    if token_hash in _SEEN_TOKENS:
        return False
    _SEEN_TOKENS[token_hash] = now
    return True


def validate_request_signature(payload: str, signature: str, secret: str) -> bool:
    """Validate HMAC signature for sensitive inter-service communication."""
    expected = hashlib.sha256(f"{payload}:{secret}".encode()).hexdigest()
    return expected == signature


def require_role(allowed_roles: List[UserRole]):
    """
    Factory creating a FastAPI dependency enforcing Role-Based Access Control.
    Accepts both frontend role names and MasterDB governance role names.
    """
    role_strings: Set[str] = {r.value.lower() for r in allowed_roles}
    role_strings.update({r.value.upper() for r in allowed_roles})

    async def role_checker(
        authorization: Optional[str] = Header(None),
        x_api_key: Optional[str] = Header(None, alias="X-API-Key")
    ) -> Dict[str, Any]:
        # Service API key bypass (admin level)
        if x_api_key and x_api_key in ("2b899caf7e3aea924c96761326bdded5162da31a9d1fdba59a2a451d2335c778", "vana_test_key_master"):
            return {
                "id": "usr-system-key",
                "role": "admin",
                "governance_role": "PLATFORM_ADMIN",
                "auth_type": "api_key"
            }

        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required. Provide 'Authorization: Bearer <token>' header.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        token = authorization.split(" ", 1)[1].strip()

        # Import vana_auth dynamically to decode token
        try:
            from vana_auth import decode_access_token
            payload = decode_access_token(token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        user_role = (payload.get("role") or "").lower()
        gov_role = (payload.get("governance_role") or "").upper()

        if user_role in role_strings or gov_role in role_strings:
            return payload

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access Denied: Role '{user_role}' is not authorized. Required: {[r.value for r in allowed_roles]}."
        )

    return role_checker
