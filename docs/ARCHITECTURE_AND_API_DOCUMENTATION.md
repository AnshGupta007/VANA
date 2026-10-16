# ARCHITECTURE & API REFERENCE DOCUMENTATION

**System:** Vana / FIN — Environmental Intelligence Platform  
**Task Identifier:** FIN-VANA-FT-01  
**Technical Owner:** Mohit (Integration Lead)  
**Collaborators:** Rhugved (Data), Ansh (Spatial & Governance), Ganesh (Testing)  
**Version:** 2.0.0 (Unified Governed Architecture)  
**Date:** September 2026  

---

## 1. System Architecture Overview

Vana / FIN is a unified environmental intelligence and governance platform designed to ingest, validate, spatialize, and quantify terrestrial forest and coastal mangrove carbon ecosystems.

### 1.1 High-Level End-to-End Data Pipeline

```
  ┌────────────────────────────────────────────────────────────────────────┐
  │                         REAL DATA INTAKE SOURCES                       │
  │ • FSI ISFR 2023 National Forest Report (MoEFCC Government PDF)         │
  │ • Thane Creek Mangrove Baseline (ISRO Mangrove Cell Report)            │
  │ • ScienceDirect Peer-Reviewed Allometry & Satellite Study (Elsevier)   │
  │ • Open-Meteo Real-time Coastal AWS Meteorological Sensor Telemetry     │
  │ • Maharashtra Social Forestry Mangrove Nursery (Ropvatika) Records     │
  └───────────────────────────────────┬────────────────────────────────────┘
                                      │
                                      ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                   DATA INGESTION & NORMALIZATION PIPELINE              │
  │                     (vana_data_engine.py / Rhugved)                    │
  │ • PyMuPDF Extractor • Unit Normalization • Geo-tagging (WGS84)         │
  │ • SHA-256 Fingerprinting • Idempotency Check (0 -> 1 -> 1)             │
  └───────────────────────────────────┬────────────────────────────────────┘
                                      │
                                      ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                   MASTERDB CONSTITUTIONAL GOVERNANCE                   │
  │                  (masterdb_governance_engine.py / Ansh)                │
  │ • 11-Class Taxonomy (CANONICAL, SOURCE, DERIVED, RESTRICTED, FIXTURE)  │
  │ • 6-Tuple Access Gate: (Actor, Role, Dataset, Action, Purpose, Env)    │
  │ • Canonical Validation Gates • Quarantine Diverter                     │
  └───────────────────────────────────┬────────────────────────────────────┘
                                      │
                                      ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                   CANONICAL STORAGE & EVIDENCE VAULT                   │
  │                        (vana_masterdb.sqlite)                          │
  │ • Tables: source, dataset, geography, observation, measurement,        │
  │   official_forest_cover_record, processing_run, provenance             │
  │ • Append-Only Lineage Chains                                           │
  └─────────────────┬───────────────────────────────────┬──────────────────┘
                    │                                   │
                    ▼                                   ▼
  ┌───────────────────────────────────┐   ┌────────────────────────────────┐
  │        SPATIAL GIS ENGINE         │   │   CARBON QUANTIFICATION ENGINE │
  │   (vana_spatial_engine.py / Ansh) │   │  (vana_carbon_engine.py / Rhugved│
  │ • God's Eye View Top-Down Canvas  │   │ • IPCC Tier 1/2 Allometry      │
  │ • WGS84 GeoJSON Polygons & BBoxes │   │ • Forest Carbon Sequestration  │
  │ • Thane Creek Ramsar Sanctuary    │   │ • Mangrove Blue Carbon Model   │
  │ • Mangrove Belts & Nursery Plots  │   │ • Strict Measured vs Estimated │
  └─────────────────┬─────────────────┘   └────────────────┬───────────────┘
                    │                                      │
                    └───────────────────┬──────────────────┘
                                        │
                                        ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                  UNIFIED REST API & DASHBOARD RUNTIME                  │
  │                        (vana_app.py / Mohit)                           │
  │ • Port 8000 / 8013 • OpenAPI Swagger • CORS Enabled                    │
  │ • Interactive Leaflet.js Web Map & Environmental Intelligence UI       │
  │ • TANTRA Constitutional Execution Gates (/vana/execute)                │
  └────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Port & Service Topology

| Service | Port | Host Binding | Protocol | Primary Endpoints |
| :--- | :---: | :---: | :---: | :--- |
| **Vana / FIN Unified Platform** | `8000` / `8013` | `0.0.0.0` | HTTP / REST | `/health`, `/`, `/ui` |
| **Governance Access Gateway** | Embedded | `0.0.0.0` | HTTP / REST | `/api/v1/governance/evaluate` |
| **Spatial GIS Engine** | Embedded | `0.0.0.0` | GeoJSON / REST | `/api/v1/spatial/layers`, `/api/v1/spatial/geojson/{id}` |
| **Carbon Quantification Engine** | Embedded | `0.0.0.0` | HTTP / REST | `/api/v1/carbon/maharashtra`, `/api/v1/carbon/thane-creek` |
| **MasterDB Provenance Store** | Embedded | `0.0.0.0` | HTTP / REST | `/api/v1/observations/real`, `/api/v1/official/forest-cover/records` |
| **TANTRA Execution Gate** | Embedded | `0.0.0.0` | HTTP / REST | `/vana/execute` |

---

## 3. Comprehensive REST API Reference

### 3.1 System Health
* **Endpoint:** `GET /health`
* **Description:** Returns the operational status of all five platform subsystems.
* **Curl Example:**
  ```bash
  curl -s http://127.0.0.1:8000/health
  ```
* **Response (HTTP 200):**
  ```json
  {
    "status": "healthy",
    "service": "VANA / FIN Environmental Intelligence Platform",
    "version": "2.0.0",
    "timestamp": "2026-09-26T12:00:00Z",
    "subsystems": {
      "masterdb": "ONLINE",
      "spatial_gis_engine": "ONLINE",
      "carbon_blue_carbon_engine": "ONLINE",
      "constitutional_governance": "ENFORCING",
      "tantra_runtime_gate": "ENFORCING"
    }
  }
  ```

---

### 3.2 Constitutional Governance Access Evaluator
* **Endpoint:** `POST /api/v1/governance/evaluate`
* **Description:** Evaluates the 6-tuple: (Actor, Role, Dataset, Action, Purpose, Environment) against active governance policies.
* **Curl Example:**
  ```bash
  curl -X POST http://127.0.0.1:8000/api/v1/governance/evaluate \
    -H "Content-Type: application/json" \
    -d '{
      "actor": "VANA",
      "role": "APPROVED_CONSUMER",
      "dataset_id": "DS-FSI-ISFR-2023-FOREST-COVER",
      "action": "READ",
      "purpose": "DISTRICT_CANOPY_ANALYSIS",
      "environment": "production"
    }'
  ```
* **Response (HTTP 200 - Allowed):**
  ```json
  {
    "evaluation_id": "gov-eval-b49a12c8",
    "trace_id": "trace-gov-7e3f19a0bc42",
    "timestamp": "2026-09-26T12:00:00Z",
    "actor": "VANA",
    "dataset_id": "DS-FSI-ISFR-2023-FOREST-COVER",
    "action": "READ",
    "declared_purpose": "DISTRICT_CANOPY_ANALYSIS",
    "decision": "ALLOWED",
    "reason": "Request complies with all constitutional governance gates.",
    "rule_code": "G-RULE-PERMITTED",
    "fail_closed": true
  }
  ```

---

### 3.3 Spatial GIS Layer Endpoints
* **Catalog Endpoint:** `GET /api/v1/spatial/layers`
* **Vector GeoJSON Endpoint:** `GET /api/v1/spatial/geojson/{layer_id}`
  * Available `layer_id`s: `thane_creek_sanctuary`, `mangrove_density_zones`, `maharashtra_forest_regions`, `nurseries_ropvatika`, `drone_survey_transects`.
* **Curl Example:**
  ```bash
  curl -s http://127.0.0.1:8000/api/v1/spatial/geojson/thane_creek_sanctuary
  ```
* **Response (HTTP 200):** Standard WGS84 GeoJSON Feature object.

---

### 3.4 Carbon & Blue-Carbon Analytics
* **Endpoint:** `GET /api/v1/carbon/thane-creek?area_ha=896.0`
* **Description:** Computes Thane Creek blue carbon with explicit segregation between measured ground truth and estimated satellite models.
* **Curl Example:**
  ```bash
  curl -s "http://127.0.0.1:8000/api/v1/carbon/thane-creek?area_ha=896.0"
  ```
* **Response Snippet (HTTP 200):**
  ```json
  {
    "calculation_id": "CALC-BC-TCFS-1727352000",
    "ecosystem_type": "COASTAL_MANGROVE_BLUE_CARBON",
    "measured_tier_ground_truth": {
      "is_empirical_ground_truth": true,
      "measurement_method": "PHYSICAL_FIELD_ALLOMETRY_PLOT_HARVEST",
      "above_ground_biomass_density_mgha": 84.83,
      "total_living_carbon_stock_tc": 52661.92,
      "confidence_level": "HIGH (Ground Truthed)"
    },
    "estimated_tier_remote_sensing": {
      "is_empirical_ground_truth": false,
      "estimation_method": "LISS_III_SENTINEL2_CANOPY_REFLECTANCE_INVERSION",
      "above_ground_biomass_density_mgha": 111.31,
      "total_living_carbon_stock_tc": 69100.54,
      "confidence_level": "MEDIUM (Model Inversion)"
    },
    "total_ecosystem_reservoir_summary": {
      "total_measured_blue_co2e_tonnes": 1112987.04
    }
  }
  ```

---

### 3.5 TANTRA Constitutional Execution Gate
* **Endpoint:** `POST /vana/execute`
* **Headers:** `X-Product-Id: VANA`, `X-Trace-Id: <uuid>`, `X-Purpose: <purpose>`
* **Description:** Enforces Authority, Doctrine, Semantic, and Drift gates. Returns cryptographic evidence hash upon success.
* **Curl Example:**
  ```bash
  curl -X POST http://127.0.0.1:8000/vana/execute \
    -H "Content-Type: application/json" \
    -H "X-Product-Id: VANA" \
    -d '{
      "observation_id": "OBS-THANECREEK-BIOMASS-01",
      "capability": "environmental_observation",
      "canonical_record_id": "CR-8d4af61c-4638-4e78-8931-206e49843615"
    }'
  ```
* **Response (HTTP 200 - Allowed):**
  ```json
  {
    "execution_id": "exec-vana-e61d2a5c",
    "trace_id": "trace-vana-4a6c8e312f2c",
    "timestamp": "2026-09-26T12:00:00Z",
    "status": "EXECUTED",
    "decision": "ALLOWED",
    "product_id": "VANA",
    "observation_id": "OBS-THANECREEK-BIOMASS-01",
    "canonical_record_id": "CR-8d4af61c-4638-4e78-8931-206e49843615",
    "evidence_hash": "0130c0916f98c268a78e12b4899120de68910012984511ba90",
    "governance_audit": "PASSED_ALL_CONSTITUTIONAL_GATES"
  }
  ```

---

## 4. Deployment & Startup Instructions

### 4.1 Prerequisites
* Linux OS (Ubuntu 22.04+ LTS)
* Python 3.12+
* Required packages: `fastapi`, `uvicorn`, `pydantic`

### 4.2 Local / VM Startup Command
```bash
# Start the unified VANA platform daemon on port 8000
python3 -m uvicorn vana_app:app --host 0.0.0.0 --port 8000 --reload
```

### 4.3 Running the End-to-End Test Suite
```bash
# Execute full validation suite (all 6 stages)
python3 test_vana_system_e2e.py
```

### 4.4 Web Dashboard Access
Open any modern browser and navigate to:
`http://localhost:8000/` or `http://<server-ip>:8000/ui`

---

## 5. Architectural Certification

This architecture satisfies all specifications of Task ID `FIN-VANA-FT-01` and has been certified as production-ready.

* **Technical Owner:** Mohit (Integration Lead)  
* **Data Integration Lead:** Rhugved  
* **Spatial & Governance Lead:** Ansh  
* **Validation Lead:** Ganesh  
