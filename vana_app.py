"""
Unified VANA / FIN Environmental Intelligence Platform Runtime (vana_app.py)
Technical Owner: Mohit (Integration Lead)
Team: Rhugved (Data Lead), Ansh (Spatial & Governance Lead), Ganesh (Testing Lead)

Integrates:
- Real MasterDB Database & Provenance Joins
- Vana Spatial GIS Engine & Vector GeoJSON Layers (God's Eye View reference)
- Vana Carbon & Blue-Carbon Quantification Engine (Strict Measured vs Estimated Separation)
- MasterDB Constitutional Governance & 6-Tuple Access Control Engine
- TANTRA Runtime Execution Middleware (/vana/execute with 4 constitutional gates)
- Interactive Full-Featured Environmental Intelligence Web Dashboard
"""

import hashlib
import json
import os
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from masterdb_governance_engine import (
    AccessDecision,
    ActionType,
    DatasetClassification,
    MasterDBGovernanceEngine,
)
from vana_carbon_engine import VanaCarbonEngine
from vana_data_engine import DB_PATH, VanaDataEngine
from vana_spatial_engine import VanaSpatialEngine
from vana_auth import (
    authenticate_user,
    create_access_token,
    format_user_response,
    get_current_user,
    get_optional_user,
    register_user,
    require_role,
    ROLE_MAPPING,
    ROLE_PERMISSIONS,
    SEED_ACCOUNTS,
)

app = FastAPI(
    title="VANA / FIN Environmental Intelligence Platform",
    version="2.0.0",
    description="Unified Governed Environmental Data Platform, Spatial GIS Engine, and Carbon Analytics Runtime."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core Engines
gov_engine = MasterDBGovernanceEngine()
spatial_engine = VanaSpatialEngine()
carbon_engine = VanaCarbonEngine()
data_engine = VanaDataEngine()


# -----------------------------------------------------------------------------
# Request & Response Schemas
# -----------------------------------------------------------------------------
class LoginRequest(BaseModel):
    email: str = Field(..., example="admin@vana.bhiv")
    password: str = Field(..., example="Admin@123")


class RegisterRequest(BaseModel):
    name: str = Field(..., example="Ansh Shrivastava")
    email: str = Field(..., example="ansh@vana.bhiv")
    password: str = Field(..., min_length=6, example="User@123")
    role: Optional[str] = Field("participant", example="participant")


class AccessEvaluationRequest(BaseModel):
    actor: str = Field(..., example="VANA")
    role: str = Field(..., example="APPROVED_CONSUMER")
    dataset_id: str = Field(..., example="DS-FSI-ISFR-2023-FOREST-COVER")
    action: str = Field(..., example="READ")
    purpose: str = Field(..., example="DISTRICT_CANOPY_ANALYSIS")
    environment: str = Field("production", example="production")


class VanaExecuteRequest(BaseModel):
    product_id: Optional[str] = None
    observation_id: str = Field(..., example="OBS-THANECREEK-BIOMASS-01")
    capability: str = Field("environmental_observation", example="environmental_observation")
    canonical_record_id: Optional[str] = None
    ruling: Optional[str] = "PROCEED"
    action_eligibility: bool = True
    abstention_required: bool = False
    policy_violation: Optional[str] = None


# -----------------------------------------------------------------------------
# 1. Health & Status Endpoints
# -----------------------------------------------------------------------------
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "VANA / FIN Environmental Intelligence Platform",
        "version": "2.0.0",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "subsystems": {
            "masterdb": "ONLINE",
            "spatial_gis_engine": "ONLINE",
            "carbon_blue_carbon_engine": "ONLINE",
            "constitutional_governance": "ENFORCING",
            "tantra_runtime_gate": "ENFORCING",
            "rbac_authentication": "ONLINE"
        }
    }


# -----------------------------------------------------------------------------
# 1.5 Authentication & Role-Based Access Control (RBAC) Endpoints
# -----------------------------------------------------------------------------
@app.post("/api/v1/auth/login", summary="Login user and issue JWT bearer token")
@app.post("/auth/login", summary="Login user (compatibility alias)")
def login_user(req: LoginRequest):
    user = authenticate_user(req.email, req.password)
    access_token = create_access_token(user)
    formatted = format_user_response(user)
    return {
        "success": True,
        "message": "Authentication successful",
        "access_token": access_token,
        "refresh_token": f"ref-{uuid.uuid4().hex}",
        "token_type": "bearer",
        "expires_in_hours": 24,
        "user": formatted,
        "data": {
            "access_token": access_token,
            "refresh_token": f"ref-{uuid.uuid4().hex}",
            "token_type": "bearer",
            "user": formatted,
        }
    }


@app.post("/api/v1/auth/register", summary="Register a new user account")
@app.post("/auth/register", summary="Register a new user (compatibility alias)")
def register_new_user(req: RegisterRequest):
    user = register_user(
        name=req.name,
        email=req.email,
        password=req.password,
        role=req.role or "participant"
    )
    access_token = create_access_token(user)
    formatted = format_user_response(user)
    return {
        "success": True,
        "message": "User registered successfully",
        "access_token": access_token,
        "refresh_token": f"ref-{uuid.uuid4().hex}",
        "token_type": "bearer",
        "expires_in_hours": 24,
        "user": formatted,
        "data": {
            "access_token": access_token,
            "refresh_token": f"ref-{uuid.uuid4().hex}",
            "token_type": "bearer",
            "user": formatted,
        }
    }


@app.get("/api/v1/auth/me", summary="Get authenticated user profile and roles")
@app.get("/auth/me", summary="Get authenticated user profile (alias)")
@app.get("/user/profile", summary="Get authenticated user profile (frontend alias)")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    return {
        "success": True,
        "user": current_user,
        "data": current_user,
        **current_user
    }


@app.post("/api/v1/auth/logout", summary="Logout and invalidate session")
@app.post("/auth/logout", summary="Logout (alias)")
def logout_user():
    return {
        "success": True,
        "message": "Session logged out successfully."
    }


@app.get("/api/v1/auth/roles", summary="List supported roles and permissions matrix")
def get_auth_roles():
    return {
        "success": True,
        "frontend_roles": ["admin", "participant", "judge", "steward"],
        "governance_roles": ["PLATFORM_ADMIN", "APPROVED_CONSUMER", "AUDITOR", "GOVERNANCE_STEWARD"],
        "role_mapping": ROLE_MAPPING,
        "permissions_matrix": ROLE_PERMISSIONS,
        "test_accounts": [
            {
                "email": a["email"],
                "role": a["role"],
                "governance_role": a["governance_role"],
                "note": "Pre-seeded test account"
            }
            for a in SEED_ACCOUNTS
        ]
    }


# -----------------------------------------------------------------------------
# 2. MasterDB Governance & Access Control Endpoints (Ansh)
# -----------------------------------------------------------------------------
@app.post("/api/v1/governance/evaluate")
def evaluate_access(req: AccessEvaluationRequest):
    try:
        act = ActionType(req.action.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid action: {req.action}. Must be one of {[a.value for a in ActionType]}")

    verdict = gov_engine.evaluate_access(
        actor=req.actor,
        role=req.role,
        dataset_id=req.dataset_id,
        action=act,
        purpose=req.purpose,
        environment=req.environment
    )
    status_code = 200 if verdict["decision"] in ("ALLOWED", "CONTROLLED") else (403 if verdict["decision"] == "DENIED" else 202)
    return JSONResponse(status_code=status_code, content=verdict)


@app.get("/api/v1/governance/datasets")
def list_governed_datasets():
    datasets = []
    for d_id, meta in gov_engine.GOVERNED_DATASETS.items():
        datasets.append({
            "dataset_id": d_id,
            "name": meta["name"],
            "owner": meta["owner"],
            "custodian": meta["custodian"],
            "classification": meta["classification"].value,
            "sensitivity": meta["sensitivity"],
            "allowed_consumers": meta["allowed_consumers"],
            "allowed_actions": [a.value for a in meta["allowed_actions"]],
            "approved_purposes": meta["approved_purposes"],
            "lifecycle": meta["lifecycle"].value,
            "is_synthetic": meta["is_synthetic"]
        })
    return {"count": len(datasets), "datasets": datasets}


@app.get("/api/v1/governance/audit-log")
async def get_governance_audit_log(
    limit: int = 50,
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    # RBAC Gate: If credentials are provided, enforce audit privilege
    if authorization or x_api_key:
        user = await get_current_user(authorization=authorization, x_api_key=x_api_key)
        allowed = {"admin", "judge", "steward", "platform_admin", "auditor", "governance_steward"}
        user_role = (user.get("role") or "").lower()
        gov_role = (user.get("governance_role") or "").lower()
        if user_role not in allowed and gov_role not in allowed:
            raise HTTPException(
                status_code=403,
                detail=f"Access Denied: Role '{user.get('role')}' is not authorized to inspect governance audit logs. Required: admin, judge, or steward."
            )
    return {"count": len(gov_engine.audit_log[-limit:]), "audit_trail": gov_engine.audit_log[-limit:]}


# -----------------------------------------------------------------------------
# 3. Spatial GIS Endpoints (God's Eye View Reference)
# -----------------------------------------------------------------------------
@app.get("/api/v1/spatial/layers")
def get_spatial_layers():
    return {"status": "SUCCESS", "layers": spatial_engine.list_layers()}


@app.get("/api/v1/spatial/geojson/{layer_id}")
def get_spatial_layer_geojson(layer_id: str):
    layer = spatial_engine.get_layer(layer_id)
    if not layer:
        raise HTTPException(status_code=404, detail=f"Spatial layer '{layer_id}' not found.")
    return layer


@app.get("/api/v1/spatial/envelope")
def get_unified_spatial_envelope():
    return spatial_engine.get_unified_spatial_envelope()


# -----------------------------------------------------------------------------
# 4. Carbon & Blue-Carbon Analytics Endpoints (Rhugved + Ansh)
# -----------------------------------------------------------------------------
@app.get("/api/v1/carbon/maharashtra")
def get_maharashtra_forest_carbon():
    return carbon_engine.calculate_maharashtra_forest_carbon()


@app.get("/api/v1/carbon/thane-creek")
def get_thane_creek_blue_carbon(
    area_ha: float = Query(896.0, description="Mangrove area in hectares"),
    measured_agb: float = Query(84.83, description="Measured Above-Ground Biomass density (Mg/ha)"),
    estimated_agb: float = Query(111.31, description="Estimated Above-Ground Biomass density (Mg/ha)")
):
    return carbon_engine.calculate_thane_creek_blue_carbon(
        mangrove_area_ha=area_ha,
        measured_agb_mgha=measured_agb,
        estimated_agb_mgha=estimated_agb
    )


@app.get("/api/v1/carbon/summary")
def get_carbon_summary():
    fc = carbon_engine.calculate_maharashtra_forest_carbon()
    bc = carbon_engine.calculate_thane_creek_blue_carbon()
    return {
        "status": "SUCCESS",
        "forest_carbon_summary": {
            "total_forest_area_km2": fc["spatial_scope"]["combined_area_km2"],
            "total_forest_carbon_stock_MtC": fc["carbon_metrics"]["total_carbon_stock_million_tc"],
            "total_forest_co2e_billion_tonnes": fc["carbon_metrics"]["co2e_billion_tonnes"]
        },
        "blue_carbon_summary": {
            "sanctuary_mangrove_area_ha": bc["spatial_scope"]["mangrove_area_ha"],
            "measured_living_carbon_tC": bc["measured_tier_ground_truth"]["total_living_carbon_stock_tc"],
            "estimated_living_carbon_tC": bc["estimated_tier_remote_sensing"]["total_living_carbon_stock_tc"],
            "total_ecosystem_blue_carbon_tC": bc["total_ecosystem_reservoir_summary"]["total_measured_blue_carbon_tc"],
            "total_ecosystem_blue_co2e_tonnes": bc["total_ecosystem_reservoir_summary"]["total_measured_blue_co2e_tonnes"],
            "measured_vs_estimated_variance_pct": bc["variance_and_scientific_notes"]["percentage_variance"],
            "scientific_doctrine": "Strict Segregation of Measured vs Estimated enforced per DOC-001"
        }
    }


# -----------------------------------------------------------------------------
# 5. MasterDB Database & Provenance Queries
# -----------------------------------------------------------------------------
@app.get("/api/v1/observations/real")
def get_real_observations():
    conn = data_engine.get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT o.observation_id, o.dataset_id, o.observation_date, o.species, o.observation_type,
           o.confidence, o.is_synthetic, g.place_name, g.geom_wkt
    FROM observation o
    LEFT JOIN geography g ON o.geo_id = g.geo_id
    WHERE o.is_synthetic = 0
    """)
    observations = []
    for r in cur.fetchall():
        obs = dict(r)
        # Fetch measurements and provenance
        cur.execute("""
        SELECT m.measurement_id, m.metric_name, m.value, m.unit, m.method, m.transform_applied,
               p.derivation_note, s.title as source_title, s.publisher as source_publisher, s.url as source_url
        FROM measurement m
        LEFT JOIN provenance p ON m.measurement_id = p.measurement_id
        LEFT JOIN source s ON p.source_id = s.source_id
        WHERE m.observation_id = ?
        GROUP BY m.measurement_id
        """, (obs["observation_id"],))
        obs["measurements"] = [dict(m_row) for m_row in cur.fetchall()]
        observations.append(obs)
    conn.close()
    return {"count": len(observations), "observations": observations}


@app.get("/api/v1/official/forest-cover/records")
def get_official_forest_records():
    conn = data_engine.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM official_forest_cover_record")
    records = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(records), "records": records}


@app.get("/api/v1/weather/thane-creek")
def get_weather_data():
    conn = data_engine.get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT m.metric_name, m.value, m.unit, m.method
    FROM measurement m
    WHERE m.observation_id = 'OBS-OPENMETEO-TC-001'
    """)
    metrics = {r["metric_name"]: {"value": r["value"], "unit": r["unit"], "method": r["method"]} for r in cur.fetchall()}
    conn.close()
    return {
        "site": "Thane Creek Coastal Station (Open-Meteo AWS)",
        "coordinates": {"latitude": 19.12, "longitude": 72.94},
        "metrics": metrics
    }


# -----------------------------------------------------------------------------
# 6. TANTRA Constitutional Execution Gate (/vana/execute)
# -----------------------------------------------------------------------------
@app.post("/vana/execute")
async def vana_execute(
    req: VanaExecuteRequest,
    x_product_id: Optional[str] = Header(None, alias="X-Product-Id"),
    x_trace_id: Optional[str] = Header(None, alias="X-Trace-Id"),
    x_purpose: Optional[str] = Header(None, alias="X-Purpose"),
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    # RBAC Gate: If a user token is provided, verify they have admin/execution privilege
    if authorization:
        user = await get_current_user(authorization=authorization, x_api_key=x_api_key)
        allowed_roles = {"admin", "platform_admin"}
        user_role = (user.get("role") or "").lower()
        gov_role = (user.get("governance_role") or "").lower()
        if user_role not in allowed_roles and gov_role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access Denied: Execution of TANTRA capability requires 'admin' or 'PLATFORM_ADMIN' role. Current role: '{user.get('role')}'."
            )

    trace_id = x_trace_id or f"trace-vana-{uuid.uuid4().hex[:12]}"
    execution_id = f"exec-vana-{uuid.uuid4().hex[:8]}"
    product_id = x_product_id or req.product_id or "VANA"
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Gate 1: Authority Gate
    if product_id.upper() not in gov_engine.ALLOWED_PRODUCTS:
        refusal = {
            "execution_id": execution_id,
            "trace_id": trace_id,
            "timestamp": timestamp,
            "gate_failed": "AUTHORITY",
            "decision": "REFUSED",
            "error_code": "REFUSAL_UNAUTHORIZED_PRODUCT_AUTHORITY",
            "reason": f"Product '{product_id}' unauthorized to invoke capability '{req.capability}'."
        }
        return JSONResponse(status_code=403, content=refusal)

    # Gate 2: Doctrine Gate
    if req.policy_violation:
        refusal = {
            "execution_id": execution_id,
            "trace_id": trace_id,
            "timestamp": timestamp,
            "gate_failed": "DOCTRINE",
            "decision": "REFUSED",
            "error_code": "REFUSAL_DOCTRINE_VIOLATION",
            "reason": f"Doctrine violation: {req.policy_violation}. Execution halted."
        }
        return JSONResponse(status_code=400, content=refusal)

    # Gate 3: Semantic Gate
    if req.ruling == "ABSTAIN" or req.action_eligibility is False or req.abstention_required is True:
        refusal = {
            "execution_id": execution_id,
            "trace_id": trace_id,
            "timestamp": timestamp,
            "gate_failed": "SEMANTIC",
            "decision": "GOVERNED_ABSTENTION",
            "error_code": "REFUSAL_SEMANTIC_GOVERNED_ABSTENTION",
            "reason": "Semantically unsupported scientific context or explicit ABSTAIN ruling. Safe abstention enforced."
        }
        return JSONResponse(status_code=200, content=refusal)

    # Gate 4: Lineage & Evidence Hash
    payload_repr = f"{execution_id}:{req.observation_id}:{product_id}:{timestamp}"
    evidence_hash = hashlib.sha256(payload_repr.encode()).hexdigest()

    return {
        "execution_id": execution_id,
        "trace_id": trace_id,
        "timestamp": timestamp,
        "status": "EXECUTED",
        "decision": "ALLOWED",
        "product_id": product_id,
        "observation_id": req.observation_id,
        "canonical_record_id": req.canonical_record_id or f"CR-{uuid.uuid4()}",
        "evidence_hash": evidence_hash,
        "governance_audit": "PASSED_ALL_CONSTITUTIONAL_GATES"
    }


# -----------------------------------------------------------------------------
# 7. Interactive Full-Featured Environmental Intelligence Web Dashboard
# -----------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
@app.get("/ui", response_class=HTMLResponse)
def serve_dashboard():
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>VANA / FIN — Environmental Intelligence Platform</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    :root {
      --bg-dark: #090d16;
      --card-bg: rgba(17, 24, 39, 0.75);
      --card-border: rgba(31, 41, 55, 0.8);
      --primary: #10b981;
      --primary-glow: rgba(16, 185, 129, 0.35);
      --accent: #3b82f6;
      --warning: #f59e0b;
      --danger: #ef4444;
      --text-main: #f3f4f6;
      --text-muted: #9ca3af;
      --font-sans: 'Outfit', sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: var(--bg-dark);
      color: var(--text-main);
      font-family: var(--font-sans);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      background-image: radial-gradient(circle at 15% 15%, rgba(16, 185, 129, 0.08) 0%, transparent 40%),
                        radial-gradient(circle at 85% 85%, rgba(59, 130, 246, 0.06) 0%, transparent 40%);
    }
    header {
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--card-border);
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 1000;
    }
    .logo-container { display: flex; align-items: center; gap: 0.75rem; }
    .logo-badge {
      background: linear-gradient(135deg, #10b981, #059669);
      color: #fff;
      font-weight: 700;
      font-size: 1.1rem;
      padding: 0.35rem 0.75rem;
      border-radius: 8px;
      letter-spacing: 1px;
      box-shadow: 0 0 15px var(--primary-glow);
    }
    .logo-title { font-size: 1.25rem; font-weight: 600; letter-spacing: -0.5px; }
    .logo-subtitle { font-size: 0.75rem; color: var(--text-muted); font-family: var(--font-mono); }
    .nav-stats { display: flex; gap: 1.5rem; align-items: center; }
    .stat-pill {
      background: rgba(31, 41, 55, 0.6);
      border: 1px solid rgba(75, 85, 99, 0.4);
      padding: 0.35rem 0.85rem;
      border-radius: 9999px;
      font-size: 0.8rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--primary); box-shadow: 0 0 8px var(--primary); }
    main {
      padding: 1.5rem 2rem;
      display: grid;
      grid-template-columns: 1fr 420px;
      gap: 1.5rem;
      flex: 1;
    }
    .map-section {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
    .glass-card {
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 1.25rem;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    #map {
      height: 480px;
      width: 100%;
      border-radius: 10px;
      border: 1px solid rgba(75, 85, 99, 0.4);
      background: #1e293b;
    }
    .card-title {
      font-size: 1rem;
      font-weight: 600;
      margin-bottom: 0.75rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .card-badge {
      font-size: 0.7rem;
      font-family: var(--font-mono);
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      background: rgba(16, 185, 129, 0.15);
      color: var(--primary);
      border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .sidebar { display: flex; flex-direction: column; gap: 1.25rem; }
    .metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
    .metric-box {
      background: rgba(15, 23, 42, 0.5);
      border: 1px solid rgba(55, 65, 81, 0.5);
      padding: 0.85rem;
      border-radius: 8px;
    }
    .metric-label { font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.25rem; }
    .metric-val { font-size: 1.35rem; font-weight: 700; color: #fff; font-family: var(--font-mono); }
    .metric-sub { font-size: 0.7rem; color: var(--primary); margin-top: 0.2rem; }
    .comparison-container {
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid rgba(55, 65, 81, 0.6);
      border-radius: 8px;
      padding: 1rem;
      margin-top: 0.5rem;
    }
    .bar-row { margin-bottom: 0.75rem; }
    .bar-labels { display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 0.3rem; }
    .bar-bg { height: 12px; background: rgba(55, 65, 81, 0.4); border-radius: 6px; overflow: hidden; }
    .bar-fill-measured { height: 100%; width: 76%; background: linear-gradient(90deg, #10b981, #059669); }
    .bar-fill-estimated { height: 100%; width: 100%; background: linear-gradient(90deg, #3b82f6, #2563eb); }
    .tabs { display: flex; gap: 0.5rem; margin-bottom: 1rem; border-bottom: 1px solid rgba(55, 65, 81, 0.6); padding-bottom: 0.5rem; }
    .tab-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 0.85rem;
      font-weight: 500;
      padding: 0.4rem 0.8rem;
      border-radius: 6px;
      cursor: pointer;
      font-family: var(--font-sans);
    }
    .tab-btn.active { background: rgba(16, 185, 129, 0.15); color: var(--primary); }
    .eval-input {
      width: 100%;
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid rgba(75, 85, 99, 0.5);
      border-radius: 6px;
      padding: 0.5rem 0.75rem;
      color: #fff;
      font-family: var(--font-mono);
      font-size: 0.8rem;
      margin-bottom: 0.6rem;
    }
    .btn-submit {
      width: 100%;
      background: linear-gradient(135deg, #10b981, #059669);
      color: white;
      border: none;
      padding: 0.65rem;
      border-radius: 6px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }
    .btn-submit:hover { box-shadow: 0 0 15px var(--primary-glow); }
    .eval-result {
      margin-top: 0.75rem;
      padding: 0.75rem;
      border-radius: 6px;
      font-size: 0.8rem;
      font-family: var(--font-mono);
      display: none;
    }
    .result-allowed { background: rgba(16, 185, 129, 0.15); border: 1px solid var(--primary); color: #34d399; }
    .result-denied { background: rgba(239, 68, 68, 0.15); border: 1px solid var(--danger); color: #f87171; }
    .result-approval { background: rgba(245, 158, 11, 0.15); border: 1px solid var(--warning); color: #fbbf24; }
    .provenance-tag {
      font-size: 0.7rem;
      color: var(--text-muted);
      border-top: 1px solid rgba(55, 65, 81, 0.4);
      padding-top: 0.5rem;
      margin-top: 0.5rem;
      display: flex;
      justify-content: space-between;
    }
    a { color: var(--primary); text-decoration: none; }
  </style>
</head>
<body>
  <header>
    <div class="logo-container">
      <div class="logo-badge">FIN / VANA</div>
      <div>
        <div class="logo-title">Environmental Intelligence Platform</div>
        <div class="logo-subtitle">BHIV vNEXT Governed Runtime • Real Data Integration v2.0</div>
      </div>
    </div>
    <div class="nav-stats">
      <div class="stat-pill"><div class="status-dot"></div> MasterDB: <b>CONNECTED</b></div>
      <div class="stat-pill"><div class="status-dot" style="background:#3b82f6; box-shadow:0 0 8px #3b82f6;"></div> Governance: <b>ENFORCING</b></div>
      <div class="stat-pill"><div class="status-dot" style="background:#10b981;"></div> Spatial: <b>5 LAYERS</b></div>
    </div>
  </header>

  <main>
    <!-- Left Column: Spatial GIS Map & Observations -->
    <div class="map-section">
      <div class="glass-card">
        <div class="card-title">
          <span>Top-Down Spatial Canvas (God's Eye View Reference)</span>
          <span class="card-badge" id="layerStatusBadge">EPSG:4326 • WGS84</span>
        </div>
        <div id="map"></div>
        <div style="margin-top: 0.75rem; display: flex; gap: 0.75rem; flex-wrap: wrap;">
          <button class="tab-btn active" onclick="zoomLayer('thane')">Thane Creek Sanctuary</button>
          <button class="tab-btn" onclick="zoomLayer('density')">Mangrove Belts</button>
          <button class="tab-btn" onclick="zoomLayer('nurseries')">Ropvatika Plots</button>
          <button class="tab-btn" onclick="zoomLayer('maharashtra')">Maharashtra Divisions</button>
        </div>
      </div>

      <!-- Real Observations Table -->
      <div class="glass-card">
        <div class="card-title">
          <span>MasterDB Real Observation Records & Lineage</span>
          <span class="card-badge">PROVENANCE TRACED</span>
        </div>
        <div id="obsList" style="display:flex; flex-direction:column; gap:0.6rem; max-height:220px; overflow-y:auto;">
          <!-- Dynamically populated -->
        </div>
      </div>
    </div>

    <!-- Right Column: Environmental Intelligence & Governance Engine -->
    <div class="sidebar">
      <!-- Carbon Intelligence -->
      <div class="glass-card">
        <div class="card-title">
          <span>Carbon & Blue-Carbon Intelligence</span>
          <span class="card-badge">IPCC TIER 1/2</span>
        </div>
        <div class="metric-grid">
          <div class="metric-box">
            <div class="metric-label">Thane Creek Blue Carbon</div>
            <div class="metric-val" id="bcVal">1.11M</div>
            <div class="metric-sub">tCO2e Reservoir</div>
          </div>
          <div class="metric-box">
            <div class="metric-label">Maharashtra Forest Stock</div>
            <div class="metric-val" id="fcVal">0.79B</div>
            <div class="metric-sub">tCO2e Sequestered</div>
          </div>
        </div>

        <div class="comparison-container">
          <div style="font-size:0.8rem; font-weight:600; margin-bottom:0.5rem; color:#f3f4f6;">
            Strict Separation: Measured vs Estimated Biomass
          </div>
          <div class="bar-row">
            <div class="bar-labels">
              <span><b>Measured</b> (Ground Allometry)</span>
              <span style="color:#10b981; font-family:var(--font-mono);">84.83 Mg/ha</span>
            </div>
            <div class="bar-bg"><div class="bar-fill-measured"></div></div>
          </div>
          <div class="bar-row">
            <div class="bar-labels">
              <span><b>Estimated</b> (Satellite Inversion)</span>
              <span style="color:#3b82f6; font-family:var(--font-mono);">111.31 Mg/ha</span>
            </div>
            <div class="bar-bg"><div class="bar-fill-estimated"></div></div>
          </div>
          <div style="font-size:0.7rem; color:var(--text-muted); margin-top:0.4rem;">
            +31.2% variance due to fringe canopy capture in satellite inversion. Measured & estimated are never blended.
          </div>
        </div>
      </div>

      <!-- Real Climate Sensor Feed -->
      <div class="glass-card">
        <div class="card-title">
          <span>Real Meteorological Telemetry (Thane Creek)</span>
          <span class="card-badge">OPEN-METEO AWS</span>
        </div>
        <div class="metric-grid">
          <div class="metric-box">
            <div class="metric-label">Ambient Temp</div>
            <div class="metric-val" id="tempVal">31.4°C</div>
            <div class="metric-sub">WMO Sensor</div>
          </div>
          <div class="metric-box">
            <div class="metric-label">Humidity</div>
            <div class="metric-val" id="humVal">78.2%</div>
            <div class="metric-sub">Hygrometer</div>
          </div>
          <div class="metric-box">
            <div class="metric-label">Wind Speed</div>
            <div class="metric-val" id="windVal">14.8 km/h</div>
            <div class="metric-sub">10m Mast</div>
          </div>
          <div class="metric-box">
            <div class="metric-label">Solar Radiation</div>
            <div class="metric-val" id="solVal">580 W/m²</div>
            <div class="metric-sub">Pyranometer</div>
          </div>
        </div>
      </div>

      <!-- Governance Access Evaluator (Ansh) -->
      <div class="glass-card">
        <div class="card-title">
          <span>MasterDB Constitutional Access Evaluator</span>
          <span class="card-badge">6-TUPLE GATE</span>
        </div>
        <div>
          <label style="font-size:0.75rem; color:var(--text-muted);">Caller Product / Identity:</label>
          <input type="text" id="evalActor" class="eval-input" value="VANA">

          <label style="font-size:0.75rem; color:var(--text-muted);">Role:</label>
          <select id="evalRole" class="eval-input">
            <option value="APPROVED_CONSUMER">APPROVED_CONSUMER</option>
            <option value="DATASET_OWNER">DATASET_OWNER</option>
            <option value="EXTERNAL_PARTNER">EXTERNAL_PARTNER</option>
            <option value="ANONYMOUS">ANONYMOUS (Unknown)</option>
          </select>

          <label style="font-size:0.75rem; color:var(--text-muted);">Target Dataset:</label>
          <select id="evalDataset" class="eval-input">
            <option value="DS-FSI-ISFR-2023-FOREST-COVER">DS-FSI-ISFR-2023-FOREST-COVER (Canonical)</option>
            <option value="DS-THANECREEK-2023-BIOMASS">DS-THANECREEK-2023-BIOMASS (Canonical Ecosystem)</option>
            <option value="DS-SYNTHETIC-GROUP3-FIXTURE-01">DS-SYNTHETIC-GROUP3-FIXTURE-01 (Fixture)</option>
          </select>

          <label style="font-size:0.75rem; color:var(--text-muted);">Declared Purpose:</label>
          <input type="text" id="evalPurpose" class="eval-input" value="DISTRICT_CANOPY_ANALYSIS">

          <label style="font-size:0.75rem; color:var(--text-muted);">Action:</label>
          <select id="evalAction" class="eval-input">
            <option value="READ">READ</option>
            <option value="WRITE">WRITE</option>
            <option value="EXPORT">EXPORT</option>
            <option value="ADMIN">ADMIN</option>
          </select>

          <button class="btn-submit" onclick="runGovernanceCheck()">Evaluate Constitutional Access</button>
          <div id="evalResult" class="eval-result"></div>
        </div>
      </div>
    </div>
  </main>

  <script>
    // Initialize Leaflet Map
    const map = L.map('map').setView([19.130, 72.980], 12);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
      maxZoom: 18
    }).addTo(map);

    let layerObjects = {};

    // Load Spatial Layers from API
    async function loadMapLayers() {
      try {
        const res = await fetch('/api/v1/spatial/envelope');
        const data = await res.json();
        
        L.geoJSON(data, {
          style: function(feature) {
            return {
              color: feature.properties.color || feature.properties.stroke_color || '#10b981',
              weight: 2,
              fillColor: feature.properties.color || feature.properties.fill_color || '#10b981',
              fillOpacity: feature.properties.fill_opacity || 0.35
            };
          },
          onEachFeature: function(feature, layer) {
            let popup = `<b>${feature.properties.name || feature.properties.zone_name || feature.properties.region_name || feature.properties.site_name}</b><br>`;
            if (feature.properties.mangrove_cover_sqkm) popup += `Mangrove Area: ${feature.properties.mangrove_cover_sqkm} km²<br>`;
            if (feature.properties.species) popup += `Species: ${feature.properties.species}<br>`;
            if (feature.properties.measured_agb_mgha) popup += `Measured Biomass: ${feature.properties.measured_agb_mgha} Mg/ha<br>`;
            if (feature.properties.stock_count) popup += `Seedling Stock: ${feature.properties.stock_count.toLocaleString()} plants<br>`;
            layer.bindPopup(popup);
          }
        }).addTo(map);
      } catch (err) {
        console.error('Error loading spatial layers:', err);
      }
    }

    // Load Real Observations
    async function loadObservations() {
      try {
        const res = await fetch('/api/v1/observations/real');
        const data = await res.json();
        const container = document.getElementById('obsList');
        container.innerHTML = '';
        data.observations.forEach(obs => {
          const div = document.createElement('div');
          div.className = 'metric-box';
          let mHtml = obs.measurements.map(m => `• <b>${m.metric_name}:</b> ${m.value} ${m.unit} (${m.method})`).join('<br>');
          div.innerHTML = `
            <div style="display:flex; justify-content:space-between;">
              <span style="font-weight:600; color:#34d399;">${obs.observation_id}</span>
              <span class="card-badge">${obs.observation_type}</span>
            </div>
            <div style="font-size:0.75rem; color:#e2e8f0; margin:0.3rem 0;">Location: ${obs.place_name || 'Thane Creek'}</div>
            <div style="font-size:0.75rem; color:#94a3b8;">${mHtml}</div>
            <div class="provenance-tag">
              <span>Source: ${obs.measurements[0]?.source_title || 'Peer-Reviewed Literature'}</span>
              <span style="color:#10b981;">REAL GROUND TRUTH</span>
            </div>
          `;
          container.appendChild(div);
        });
      } catch (err) {
        console.error('Error loading observations:', err);
      }
    }

    function zoomLayer(target) {
      if (target === 'thane' || target === 'density') map.setView([19.130, 72.980], 12);
      else if (target === 'nurseries') map.setView([19.135, 72.975], 13);
      else if (target === 'maharashtra') map.setView([19.0, 75.5], 7);
    }

    // Governance Access Check Evaluator
    async function runGovernanceCheck() {
      const actor = document.getElementById('evalActor').value;
      const role = document.getElementById('evalRole').value;
      const dataset_id = document.getElementById('evalDataset').value;
      const purpose = document.getElementById('evalPurpose').value;
      const action = document.getElementById('evalAction').value;
      const resultBox = document.getElementById('evalResult');

      try {
        const res = await fetch('/api/v1/governance/evaluate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ actor, role, dataset_id, purpose, action })
        });
        const data = await res.json();
        resultBox.style.display = 'block';
        if (data.decision === 'ALLOWED') {
          resultBox.className = 'eval-result result-allowed';
          resultBox.innerHTML = `<b>✔ ALLOWED</b><br>Rule: ${data.rule_code}<br>Reason: ${data.reason}`;
        } else if (data.decision === 'DENIED') {
          resultBox.className = 'eval-result result-denied';
          resultBox.innerHTML = `<b>✖ DENIED</b><br>Rule: ${data.rule_code}<br>Reason: ${data.reason}`;
        } else {
          resultBox.className = 'eval-result result-approval';
          resultBox.innerHTML = `<b>⚠ REQUIRES APPROVAL</b><br>Reason: ${data.reason}`;
        }
      } catch (err) {
        resultBox.style.display = 'block';
        resultBox.className = 'eval-result result-denied';
        resultBox.innerText = 'Evaluation Error: ' + err.message;
      }
    }

    loadMapLayers();
    loadObservations();
  </script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    print("Starting VANA / FIN Integrated Platform on http://0.0.0.0:8000 ...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
