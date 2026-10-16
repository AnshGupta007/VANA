# VANA / FIN Environmental Intelligence Platform — Backend

**Task ID:** FIN-VANA-FT-01 & MASTERDB Data Governance  
**Backend System Directory:** `/media/ubuntu/New Volume/project/VANA/backend`  
**Runtime:** Python 3.12+ (FastAPI + Uvicorn + SQLite/PostgreSQL)  
**Status:** **100% OPERATIONAL & VERIFIED**  

---

## 1. Directory Structure

```
backend/
├── vana_app.py                     # Unified FastAPI application, REST endpoints, and Leaflet Web Dashboard
├── masterdb_governance_engine.py   # Constitutional Governance Engine (6-tuple access matrix & 11-class taxonomy)
├── vana_data_engine.py             # Real-data ingestion & validation pipeline (FSI, Thane Creek, Open-Meteo)
├── vana_spatial_engine.py          # Spatial GIS GeoJSON layers (God's Eye View reference, closed polygons)
├── vana_carbon_engine.py           # IPCC Tier 1/2 models (Strict Measured vs Estimated separation)
├── test_vana_system_e2e.py         # Full 6-stage end-to-end regression & integration test suite
├── vana_masterdb.sqlite            # Canonical MasterDB SQLite database with real observations & provenance
│
├── docs/                           # Complete Constitutional Governance & System Closure Deliverables
│   ├── MASTERDB_GOVERNANCE_MODEL.md             (D1 Governance Charter & Separation of Concerns)
│   ├── DATASET_GOVERNANCE_PROFILE.md            (D2 Real Dataset Profiles for FSI & Thane Creek)
│   ├── MASTERDB_ACCESS_CONTROL_MATRIX.md        (D3 21-Scenario 6-Tuple Access Evaluation Matrix)
│   ├── MASTERDB_GOVERNANCE_GAP_REPORT.md        (D4 13-Dimension Inspection, 4 Exercises, 3 Gates)
│   ├── VIJAY_TO_MOHIT_HANDOVER_CLOSURE.md       (Handover transition contract from Vijay to Mohit)
│   ├── CURRENT_STATE_TECHNICAL_AUDIT.md         (Component audit, dead path removals, ports)
│   ├── REAL_DATA_SOURCE_REGISTRY.md             (Classification into REAL, SIMULATED, UNAVAILABLE)
│   ├── SPATIAL_GIS_GODS_EYE_VIEW_INTEGRATION.md (Spatial evaluation & WGS84 GeoJSON specs)
│   ├── CARBON_BLUE_CARBON_ENGINE.md             (Carbon formulations & measured vs estimated doctrine)
│   ├── TEST_AND_EVIDENCE_REPORT.md              (Ganesh's comprehensive test & evidence report)
│   ├── ARCHITECTURE_AND_API_DOCUMENTATION.md    (Pipeline diagrams, port mappings, curl examples)
│   └── FINAL_GAP_AND_CLOSURE_REPORT.md          (Final P0 truth-state matrix & handover sign-off)
```

---

## 2. Quickstart & Verification Commands

All commands can be run directly from inside the `backend/` directory:

```bash
cd "/media/ubuntu/New Volume/project/VANA/backend"

# 1. Run Governance Engine & Proof Gate Tests
python3 masterdb_governance_engine.py

# 2. Run Real-Data Ingestion Pipeline
python3 vana_data_engine.py

# 3. Run Carbon Quantification Math Tests
python3 vana_carbon_engine.py

# 4. Run Spatial GIS Layer Checks
python3 vana_spatial_engine.py

# 5. Run the Complete End-to-End System Test Suite (All 6 Stages)
python3 test_vana_system_e2e.py

# 6. Start the Live Server & Web Dashboard
python3 -m uvicorn vana_app:app --host 0.0.0.0 --port 8000 --reload
```

---

## 3. Endpoints Overview

| Method | Path | Function |
| :--- | :--- | :--- |
| `GET` | `/health` | Subsystem health probe (`ONLINE` / `ENFORCING`) |
| `GET` | `/` or `/ui` | Full-featured interactive Leaflet web dashboard & intelligence viewer |
| `POST` | `/api/v1/governance/evaluate` | Evaluates 6-tuple `(Actor, Role, Dataset, Action, Purpose, Env)` |
| `GET` | `/api/v1/governance/datasets` | Governed dataset catalog with metadata & ownership |
| `GET` | `/api/v1/spatial/layers` | GIS layers catalog |
| `GET` | `/api/v1/spatial/geojson/{layer_id}` | Exact WGS84 vector GeoJSON feature |
| `GET` | `/api/v1/spatial/envelope` | Unified multi-layer FeatureCollection for map rendering |
| `GET` | `/api/v1/carbon/maharashtra` | Maharashtra state forest carbon calculation ($0.79\text{B } t\text{CO}_2e$) |
| `GET` | `/api/v1/carbon/thane-creek` | Thane Creek blue carbon with measured vs estimated breakdown |
| `GET` | `/api/v1/carbon/summary` | Executive carbon intelligence summary |
| `GET` | `/api/v1/observations/real` | Real MasterDB observation records with measurements & provenance joins |
| `GET` | `/api/v1/weather/thane-creek` | Real-time Open-Meteo meteorological telemetry for Thane Creek |
| `POST` | `/vana/execute` | TANTRA constitutional execution gate (Authority, Doctrine, Semantic, Drift) |
