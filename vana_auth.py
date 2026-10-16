"""
VANA / MASTERDB Authentication and Role-Based Access Control (RBAC) Engine
Author: VANA Platform Architecture Team
Compatibility: FastAPI, PyJWT, SQLite3, Hackaverse Frontend & TANTRA Pipeline

Provides:
- SQLite User Store with Salted PBKDF2 Password Hashing
- JWT Bearer Token Generation & Validation (HS256)
- Role Mapping between Frontend Roles (admin, participant, judge, steward)
  and MasterDB Governance Roles (PLATFORM_ADMIN, APPROVED_CONSUMER, AUDITOR, GOVERNANCE_STEWARD)
- Pre-seeded Test Accounts for Immediate Frontend Testing
- FastAPI Dependency Injection for Authenticated User and RBAC Enforcement
"""

import base64
import hashlib
import json
import logging
import os
import secrets
import sqlite3
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

logger = logging.getLogger("vana_auth")

DB_PATH = os.path.join(os.path.dirname(__file__), "vana_masterdb.sqlite")
JWT_SECRET = os.getenv("JWT_SECRET", "vana-constitutional-governance-secret-key-2026-prod")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
DEFAULT_API_KEY = os.getenv("API_KEY", "2b899caf7e3aea924c96761326bdded5162da31a9d1fdba59a2a451d2335c778")

# -----------------------------------------------------------------------------
# Role Definitions & Mappings
# -----------------------------------------------------------------------------
ROLE_MAPPING = {
    # Frontend Role -> MasterDB Governance Role
    "admin": "PLATFORM_ADMIN",
    "participant": "APPROVED_CONSUMER",
    "researcher": "APPROVED_CONSUMER",
    "judge": "AUDITOR",
    "auditor": "AUDITOR",
    "steward": "GOVERNANCE_STEWARD",
    "governance_steward": "GOVERNANCE_STEWARD",
    # Direct Governance Roles supported as aliases
    "PLATFORM_ADMIN": "PLATFORM_ADMIN",
    "APPROVED_CONSUMER": "APPROVED_CONSUMER",
    "AUDITOR": "AUDITOR",
    "GOVERNANCE_STEWARD": "GOVERNANCE_STEWARD",
    "EXTERNAL_PARTNER": "EXTERNAL_PARTNER",
}

ROLE_PERMISSIONS: Dict[str, Dict[str, bool]] = {
    "PLATFORM_ADMIN": {
        "view_all_datasets": True,
        "view_observations": True,
        "view_carbon_analytics": True,
        "view_spatial_layers": True,
        "view_audit_logs": True,
        "execute_tantra_pipeline": True,
        "manage_users": True,
        "evaluate_governance": True,
        "modify_policies": True,
    },
    "APPROVED_CONSUMER": {
        "view_all_datasets": True,
        "view_observations": True,
        "view_carbon_analytics": True,
        "view_spatial_layers": True,
        "view_audit_logs": False,
        "execute_tantra_pipeline": False,
        "manage_users": False,
        "evaluate_governance": True,
        "modify_policies": False,
    },
    "AUDITOR": {
        "view_all_datasets": True,
        "view_observations": True,
        "view_carbon_analytics": True,
        "view_spatial_layers": True,
        "view_audit_logs": True,
        "execute_tantra_pipeline": False,
        "manage_users": False,
        "evaluate_governance": True,
        "modify_policies": False,
    },
    "GOVERNANCE_STEWARD": {
        "view_all_datasets": True,
        "view_observations": True,
        "view_carbon_analytics": True,
        "view_spatial_layers": True,
        "view_audit_logs": True,
        "execute_tantra_pipeline": False,
        "manage_users": False,
        "evaluate_governance": True,
        "modify_policies": True,
    },
    "EXTERNAL_PARTNER": {
        "view_all_datasets": False,
        "view_observations": True,
        "view_carbon_analytics": True,
        "view_spatial_layers": True,
        "view_audit_logs": False,
        "execute_tantra_pipeline": False,
        "manage_users": False,
        "evaluate_governance": False,
        "modify_policies": False,
    },
}

# Pre-seeded Standard Test Accounts
SEED_ACCOUNTS = [
    {
        "id": "usr-admin-001",
        "user_id": "usr-admin-001",
        "email": "admin@vana.bhiv",
        "name": "VANA Platform Administrator",
        "password": "Admin@123",
        "role": "admin",
        "governance_role": "PLATFORM_ADMIN",
    },
    {
        "id": "usr-researcher-001",
        "user_id": "usr-researcher-001",
        "email": "researcher@vana.bhiv",
        "name": "Environmental Science Researcher",
        "password": "User@123",
        "role": "participant",
        "governance_role": "APPROVED_CONSUMER",
    },
    {
        "id": "usr-participant-001",
        "user_id": "usr-participant-001",
        "email": "participant@vana.bhiv",
        "name": "VANA Hackathon Participant",
        "password": "User@123",
        "role": "participant",
        "governance_role": "APPROVED_CONSUMER",
    },
    {
        "id": "usr-judge-001",
        "user_id": "usr-judge-001",
        "email": "judge@vana.bhiv",
        "name": "VANA Scientific Judge & Auditor",
        "password": "Judge@123",
        "role": "judge",
        "governance_role": "AUDITOR",
    },
    {
        "id": "usr-steward-001",
        "user_id": "usr-steward-001",
        "email": "steward@vana.bhiv",
        "name": "MasterDB Governance Steward",
        "password": "Steward@123",
        "role": "steward",
        "governance_role": "GOVERNANCE_STEWARD",
    },
]


# -----------------------------------------------------------------------------
# Security & Crypto Helpers
# -----------------------------------------------------------------------------
def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Generate salted PBKDF2-HMAC-SHA256 password hash."""
    if not salt:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return key.hex(), salt


def verify_password(stored_hash: str, salt: str, password: str) -> bool:
    """Verify password against salted PBKDF2 hash."""
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return secrets.compare_digest(key.hex(), stored_hash)


def create_access_token(user_data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate standard JWT token using pyjwt with fallback to HMAC-SHA256."""
    now = datetime.utcnow()
    expire = now + (expires_delta if expires_delta else timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))

    payload = {
        "sub": user_data["user_id"],
        "user_id": user_data["user_id"],
        "email": user_data["email"],
        "name": user_data.get("name", ""),
        "role": user_data.get("role", "participant"),
        "governance_role": user_data.get("governance_role", "APPROVED_CONSUMER"),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": "vana-auth-authority",
    }

    try:
        import jwt
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return token
    except Exception:
        # Robust fallback: standard JWT structure header.payload.signature
        header = json.dumps({"alg": "HS256", "typ": "JWT"}).encode()
        payload_bytes = json.dumps(payload).encode()
        h_b64 = base64.urlsafe_b64encode(header).decode().rstrip("=")
        p_b64 = base64.urlsafe_b64encode(payload_bytes).decode().rstrip("=")
        to_sign = f"{h_b64}.{p_b64}".encode()
        sig = hashlib.sha256(to_sign + JWT_SECRET.encode()).digest()
        s_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")
        return f"{h_b64}.{p_b64}.{s_b64}"


def decode_access_token(token: str) -> dict:
    """Decode and validate JWT token."""
    try:
        import jwt
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception as e:
        # Fallback manual decoder
        try:
            parts = token.split(".")
            if len(parts) != 3:
                raise ValueError("Malformed token")
            h_b64, p_b64, s_b64 = parts
            to_sign = f"{h_b64}.{p_b64}".encode()
            expected_sig = hashlib.sha256(to_sign + JWT_SECRET.encode()).digest()
            calc_b64 = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")
            if not secrets.compare_digest(calc_b64, s_b64):
                raise ValueError("Invalid signature")

            padding = "=" * (-len(p_b64) % 4)
            payload_json = base64.urlsafe_b64decode(p_b64 + padding).decode("utf-8")
            payload = json.loads(payload_json)

            if payload.get("exp") and payload["exp"] < time.time():
                raise ValueError("Token expired")
            return payload
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )


# -----------------------------------------------------------------------------
# Database Setup & User Management
# -----------------------------------------------------------------------------
def init_auth_db(db_path: str = DB_PATH):
    """Initialize users and sessions tables in SQLite and seed standard accounts."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        user_id TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT NOT NULL,
        governance_role TEXT NOT NULL,
        created_at TEXT NOT NULL,
        last_login TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        refresh_token TEXT UNIQUE NOT NULL,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        revoked INTEGER DEFAULT 0
    );
    """)
    conn.commit()

    # Seed default accounts if missing
    for account in SEED_ACCOUNTS:
        cur.execute("SELECT id FROM users WHERE email = ?", (account["email"],))
        if not cur.fetchone():
            p_hash, salt = hash_password(account["password"])
            now_iso = datetime.utcnow().isoformat()
            cur.execute("""
            INSERT INTO users (id, user_id, email, name, password_hash, salt, role, governance_role, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account["id"],
                account["user_id"],
                account["email"],
                account["name"],
                p_hash,
                salt,
                account["role"],
                account["governance_role"],
                now_iso
            ))
    conn.commit()
    conn.close()


def get_user_by_email(email: str, db_path: str = DB_PATH) -> Optional[dict]:
    """Retrieve user record by email."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: str, db_path: str = DB_PATH) -> Optional[dict]:
    """Retrieve user record by user_id."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ? OR id = ?", (user_id, user_id))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def register_user(
    name: str,
    email: str,
    password: str,
    role: str = "participant",
    db_path: str = DB_PATH
) -> dict:
    """Register a new user in the database."""
    email_clean = email.strip().lower()
    existing = get_user_by_email(email_clean, db_path)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{email_clean}' already exists."
        )

    # Normalize role
    role_clean = role.strip().lower()
    gov_role = ROLE_MAPPING.get(role_clean) or ROLE_MAPPING.get(role.strip().upper(), "APPROVED_CONSUMER")

    user_id = f"usr-{uuid.uuid4().hex[:10]}"
    p_hash, salt = hash_password(password)
    now_iso = datetime.utcnow().isoformat()

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO users (id, user_id, email, name, password_hash, salt, role, governance_role, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, user_id, email_clean, name.strip(), p_hash, salt, role_clean, gov_role, now_iso))
    conn.commit()
    conn.close()

    return {
        "id": user_id,
        "user_id": user_id,
        "email": email_clean,
        "name": name.strip(),
        "role": role_clean,
        "governance_role": gov_role,
        "created_at": now_iso,
    }


def authenticate_user(email: str, password: str, db_path: str = DB_PATH) -> dict:
    """Verify credentials and return user info."""
    user = get_user_by_email(email, db_path)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(user["password_hash"], user["salt"], password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.utcnow().isoformat(), user["id"]))
    conn.commit()
    conn.close()

    return user


def format_user_response(user: dict) -> dict:
    """Format user dictionary for API response."""
    gov_role = user.get("governance_role") or ROLE_MAPPING.get(user.get("role", "participant"), "APPROVED_CONSUMER")
    return {
        "id": user.get("id") or user.get("user_id"),
        "user_id": user.get("user_id") or user.get("id"),
        "email": user.get("email"),
        "name": user.get("name"),
        "role": user.get("role", "participant"),
        "governance_role": gov_role,
        "permissions": ROLE_PERMISSIONS.get(gov_role, {}),
        "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={user.get('email')}",
        "created_at": user.get("created_at"),
    }


# -----------------------------------------------------------------------------
# FastAPI Dependency Injection
# -----------------------------------------------------------------------------
async def get_current_user(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> dict:
    """
    Authenticate caller via Bearer JWT token or X-API-Key header.
    Returns user payload dictionary.
    """
    # 1. Check for system API Key (Service-to-Service integration)
    if x_api_key and x_api_key == DEFAULT_API_KEY:
        return {
            "id": "usr-system-api-key",
            "user_id": "usr-system-api-key",
            "email": "system@vana.bhiv",
            "name": "VANA Internal Service / API Key",
            "role": "admin",
            "governance_role": "PLATFORM_ADMIN",
            "permissions": ROLE_PERMISSIONS["PLATFORM_ADMIN"],
            "auth_type": "api_key",
        }

    # 2. Check for Bearer token
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide 'Authorization: Bearer <token>' or valid 'X-API-Key'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format. Must be 'Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ", 1)[1].strip()
    payload = decode_access_token(token)

    # Verify user exists in DB
    user = get_user_by_id(payload.get("user_id", payload.get("sub", "")))
    if not user:
        # Fallback to token payload if user was created dynamically
        user = {
            "id": payload.get("user_id", "unknown"),
            "user_id": payload.get("user_id", "unknown"),
            "email": payload.get("email", ""),
            "name": payload.get("name", "Authenticated User"),
            "role": payload.get("role", "participant"),
            "governance_role": payload.get("governance_role", "APPROVED_CONSUMER"),
            "created_at": datetime.utcnow().isoformat(),
        }

    formatted = format_user_response(user)
    formatted["auth_type"] = "jwt"
    return formatted


async def get_optional_user(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> Optional[dict]:
    """Retrieve user if token/key is present, else None without raising 401."""
    if not authorization and not x_api_key:
        return None
    try:
        return await get_current_user(authorization=authorization, x_api_key=x_api_key)
    except HTTPException:
        return None


def require_role(allowed_roles: List[str]):
    """
    Factory creating a FastAPI dependency enforcing Role-Based Access Control.
    Matches either frontend roles ('admin', 'participant', 'judge', 'steward')
    or MasterDB governance roles ('PLATFORM_ADMIN', 'APPROVED_CONSUMER', etc.).
    """
    normalized_allowed = set()
    for r in allowed_roles:
        normalized_allowed.add(r.lower())
        gov_match = ROLE_MAPPING.get(r.lower()) or ROLE_MAPPING.get(r.upper())
        if gov_match:
            normalized_allowed.add(gov_match.upper())

    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = (current_user.get("role") or "").lower()
        gov_role = (current_user.get("governance_role") or "").upper()

        if user_role in normalized_allowed or gov_role in normalized_allowed:
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Access Denied: Role '{user_role}' (governance: '{gov_role}') is not authorized. "
                f"Required role(s): {allowed_roles}."
            )
        )

    return role_checker


# Auto-initialize database on import
init_auth_db()
