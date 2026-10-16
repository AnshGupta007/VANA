# CURRENT-STATE TECHNICAL AUDIT & ARCHITECTURE INVENTORY

**Task Identifier:** FIN-VANA-FT-01  
**Technical Owner:** Mohit (Integration Lead)  
**Team:** Rhugved, Ansh, Ganesh  
**Scope:** Complete Codebase, APIs, Databases, Models, and Runtime Environments  
**Date:** September 2026  

---

## 1. Executive Summary

This document establishes the verified technical baseline of the **Vana / FIN** platform following the handover from Vijay Dhavan. It details what components are actively functional, what components are partially functional, what dead code was excised, and how the target unified runtime is structured.

---

## 2. Component-by-Component Technical Inventory

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                CURRENT-STATE INVENTORY MATRIX                                   │
├────────────────────┬─────────────────────┬─────────────────┬────────────────────────────────────┤
│ Component / Layer  │ Code Path           │ Truth State     │ Verified Operational Capability    │
├────────────────────┼─────────────────────┼─────────────────┼────────────────────────────────────┤
│ 1. MasterDB Core   │ bhiv-vana-masterdb- │ WORKING         │ Schema v0.9.4 in SQLite/Postgres.   │
│    Engine          │ foundation/         │                 │ Tables: source, dataset, geography,│
│                    │ vana_db.py          │                 │ observation, measurement,          │
│                    │                     │                 │ official_forest_cover_record,      │
│                    │                     │                 │ raw_artifact, provenance.          │
├────────────────────┼─────────────────────┼─────────────────┼────────────────────────────────────┤
│ 2. MasterDB API    │ bhiv-vana-masterdb- │ WORKING         │ FastAPI app on port 8013 / 8000.   │
│    Gateway         │ foundation/api/     │                 │ Endpoints: /health, /observations, │
│                    │ main.py             │                 │ /official/forest-cover,            │
│                    │                     │                 │ /datasets/{id}/forest-cover.       │
├────────────────────┼─────────────────────┼─────────────────┼────────────────────────────────────┤
│ 3. SANSKAR &       │ sanskar_adapter.py  │ WORKING         │ Ingests peer-reviewed literature;  │
│    Samachar Bridge │ samachar_science_   │                 │ normalizes biomass measurements to │
│                    │ bridge.py           │                 │ Mg/ha; joins provenance to run IDs.│
├────────────────────┼─────────────────────┼─────────────────┼────────────────────────────────────┤
│ 4. Constitutional  │ group4_constitu-    │ WORKING         │ Evaluates 4 gates: Authority,      │
│    Engine          │ tional_engine.py    │                 │ Doctrine, Semantic, Drift. Emits   │
│                    │                     │                 │ immutable refusal artifacts on fail│
├────────────────────┼─────────────────────┼─────────────────┼────────────────────────────────────┤
│ 5. Plant Image     │ Plant-Intelligence- │ ADAPTED         │ ResNet50 + YOLO models detect crop │
│    Inference       │ Capability / app/   │ (CV ONLY)       │ species and leaf stress. GIS claim │
│                    │                     │                 │ removed; repositioned as leaf CV.  │
├────────────────────┼─────────────────────┼─────────────────┼────────────────────────────────────┤
│ 6. Spatial / GIS   │ God's Eye View /    │ WORKING         │ Vector GeoJSON polygon layers for  │
│    Layer           │ vana_spatial_       │ (NEW INTEGRATED)│ Thane Creek Sanctuary, Maharashtra │
│                    │ engine.py           │                 │ Forest divisions & nursery plots.  │
├────────────────────┼─────────────────────┼─────────────────┼────────────────────────────────────┤
│ 7. Carbon Engine   │ vana_carbon_        │ WORKING         │ Calculates Forest Carbon & Blue    │
│                    │ engine.py           │ (NEW INTEGRATED)│ Carbon with strict separation of   │
│                    │                     │                 │ measured vs estimated metrics.     │
├────────────────────┼─────────────────────┼─────────────────┼────────────────────────────────────┤
│ 8. Unified Runtime │ vana_app.py         │ WORKING         │ Unified FastAPI application serving│
│    & Dashboard     │                     │ (NEW INTEGRATED)│ APIs, spatial GeoJSON, carbon math,│
│                    │                     │                 │ and interactive Leaflet web UI.    │
└────────────────────┴─────────────────────┴─────────────────┴────────────────────────────────────┘
```

---

## 3. Identification & Removal of Dead / Broken Paths

During the audit, the following dead, obsolete, or broken artifacts were identified and quarantined:

1. **Dead Windows Virtual Environment:** `.venv/` at workspace root was created with Windows batch files (`Scripts/activate.bat`) and failed under Linux (`bash: .venv/bin/python: No such file or directory`). Fixed: Switched to Linux native `/usr/bin/python3` (Python 3.12.3) with pre-installed FastAPI, Uvicorn, and Pydantic.
2. **Duplicate Ingestion Scripts:** Multiple uncoordinated scripts (`test_group2_correlation.py`, `group2_context_validator.py`, `demo_pipeline.py`) had overlapping table initialization calls that conflicted with MasterDB migrations. Remediation: Centralized database initialization through `api.db.initialize_database()`.
3. **Unvalidated Mock Ingestion:** Several tests were injecting `dataset_id="NULL"` and unclassified mock dictionaries directly into SQLite without foreign keys. Remediation: Enabled `PRAGMA foreign_keys = ON;` across all connections.

---

## 4. Port & Service Topology

| Service Name | Port | Protocol | Binding Host | Authentication | Health Check Path |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Unified VANA / FIN Runtime** | `8000` / `8013` | HTTP / REST | `0.0.0.0` | Header Token + Scope | `GET /health` |
| **Spatial GeoJSON Engine** | Embedded | REST / GeoJSON | `0.0.0.0` | Public / Scoped | `GET /api/v1/spatial/layers` |
| **Carbon Intelligence Engine** | Embedded | REST / JSON | `0.0.0.0` | Whitelisted Consumer | `GET /api/v1/carbon/summary` |
| **Interactive FIN Dashboard UI** | Embedded | HTML5 / Leaflet | `0.0.0.0` | Browser Session | `GET /` or `GET /ui` |

---

## 5. Audit Conclusion

The system has transitioned from a disconnected multi-process setup with misleading capability claims to a **lean, unified, and strictly verified architecture**. All dead paths have been eliminated, and real datasets are now connected directly to the storage, analytics, and spatial presentation tiers.
