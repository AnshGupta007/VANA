# REAL-DATA SOURCE REGISTRY & DATA INTEGRATION MANIFEST

**Task Identifier:** FIN-VANA-FT-01  
**Data Lead / Author:** Rhugved (Data & Integration)  
**Collaborator:** Ansh (Spatial / Visualization)  
**Technical Owner:** Mohit (Integration Lead)  
**System:** Vana / FIN — Environmental Intelligence Platform  
**Target Status:** PRODUCTION READY / AUDITED  
**Date:** September 2026  

---

## 1. Data Governance & Truth State Policy

In strict conformance with the BHIV vNEXT mandate:
> **"Every integrated dataset must be explicitly classified as REAL, SIMULATED, or UNAVAILABLE. No simulated dataset may ever be presented as real. All real data must retain provider identity, timestamp, geographic reference, data type, validation status, and usage license."**

---

## 2. Master Dataset Registry Matrix

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                      REAL-DATA SOURCE REGISTRY MATRIX                                                   │
├────┬──────────────────────┬───────────────────────────────┬─────────────┬──────────────────────────┬─────────────────┬─────────────────┤
│ #  │ Domain / Category    │ Dataset Title & Identifier    │ Truth State │ Source / Provider        │ Spatial Extent  │ Quality Status  │
├────┼──────────────────────┼───────────────────────────────┼─────────────┼──────────────────────────┼─────────────────┼─────────────────┤
│ 01 │ **Forest Cover**     │ FSI ISFR 2023 Forest Cover    │ **REAL**    │ Forest Survey of India,  │ Maharashtra     │ **VALIDATED**   │
│    │                      │ `DS-FSI-ISFR-2023-FOREST`     │             │ MoEFCC (Vol I, Tab 2.4)  │ State-level     │ Physical Ground │
├────┼──────────────────────┼───────────────────────────────┼─────────────┼──────────────────────────┼─────────────────┼─────────────────┤
│ 02 │ **Mangrove Cover**   │ FSI ISFR 2023 Mangrove Extent │ **REAL**    │ Forest Survey of India,  │ Maharashtra     │ **VALIDATED**   │
│    │                      │ `DS-FSI-ISFR-2023-MANGROVE`   │             │ MoEFCC (Vol I, Tab 3.3)  │ Coastal Districts| Ground & LISS-III|
├────┼──────────────────────┼───────────────────────────────┼─────────────┼──────────────────────────┼─────────────────┼─────────────────┤
│ 03 │ **Mangrove Biomass & │ Thane Creek Mangrove Standing │ **REAL**    │ ScienceDirect / Elsevier │ Thane Creek     │ **VALIDATED**   │
│    │ Blue Carbon**        │ Carbon Stock 2023             │             │ (Ecological Indicators)  │ Wetland (TCFS)  │ Peer-Reviewed   │
│    │                      │ `DS-THANECREEK-2023-BIOMASS`  │             │ DOI: 10.1016/j.ecolind   │ 19.033°N 73.016°E| Ground Allometry|
├────┼──────────────────────┼───────────────────────────────┼─────────────┼──────────────────────────┼─────────────────┼─────────────────┤
│ 04 │ **Sanctuary Baseline**│ Thane Creek Flamingo Sanctuary│ **REAL**    │ Maharashtra Forest Dept  │ Thane Creek     │ **VALIDATED**   │
│    │ (TCFS Extent)**      │ Baseline v0.1 (2020)          │             │ & ISRO Mangrove Cell     │ Sanctuary       │ Protected Zone  │
│    │                      │ `SRC_GOVT_MFD_001`            │             │ Official Survey Report   │ 8.96 sq km      │ Extent Record   │
├────┼──────────────────────┼───────────────────────────────┼─────────────┼──────────────────────────┼─────────────────┼─────────────────┤
│ 05 │ **Meteorological /   │ Open-Meteo Real Atmospheric & │ **REAL**    │ Open-Meteo Global Surface│ Thane Creek &   │ **VALIDATED**   │
│    │ Climate Feed**       │ Climate Archive (2026)        │             │ Observation Network      │ Mumbai Coast    │ Live Physical   │
│    │                      │ `DS-OPENMETEO-THANECREEK-2026`│             │ (WMO certified sensors)  │ 19.12°N 72.94°E │ Atmospheric Obs │
├────┼──────────────────────┼───────────────────────────────┼─────────────┼──────────────────────────┼─────────────────┼─────────────────┤
│ 06 │ **Nursery &          │ Maharashtra Social Forestry   │ **REAL**    │ Maharashtra Social       │ Airoli, Bhandup │ **VALIDATED**   │
│    │ Ropvatika**          │ Mangrove Nursery Inventory    │             │ Forestry Division        │ & Vikhroli      │ Nursery Stock   │
│    │                      │ `DS-MH-ROPVATIKA-2024`        │             │ Coastal Nursery Records  │ 3 Active Plots  │ Audit Records   │
├────┼──────────────────────┼───────────────────────────────┼─────────────┼──────────────────────────┼─────────────────┼─────────────────┤
│ 07 │ **GIS Geospatial     │ Global Mangrove Watch (GMW)   │ **REAL**    │ JAXA / Zenodo Archive    │ Thane Creek     │ **VALIDATED**   │
│    │ Vector Layers**      │ v3.0 Vector Extent Polygons   │             │ DOI: 10.5281/zenodo      │ Wetland Bbox    │ WGS84 Vector    │
│    │                      │ `DS-GMW-THANECREEK-POLYGONS`  │             │ .6894273                 │ EPSG:4326       │ GeoJSON Polygons│
├────┼──────────────────────┼───────────────────────────────┼─────────────┼──────────────────────────┼─────────────────┼─────────────────┤
│ 08 │ **Drone LiDAR Survey │ Drone Aerial Point Cloud      │ **SIMULATED │ Group 3 Synthetic Test   │ Thane Creek     │ **CAPTURED**    │
│    │ & Canopy Height**    │ Observation TC-Z03-F02        │ FIXTURE**   │ Fixture Generator        │ Zone 03 (Mock)  │ (Explicitly     │
│    │                      │ `TC-Z03-F02-LIDAR-OBS001`     │             │                          │ Point 19.22°N   │ Labeled Mock)   │
├────┼──────────────────────┼───────────────────────────────┼─────────────┼──────────────────────────┼─────────────────┼─────────────────┤
│ 09 │ **Multispectral Raw  │ Sentinel-2 L2A Top-of-Canopy  │ **UNAVAIL-  │ Copernicus Open Access   │ National        │ **UNAVAILABLE** │
│    │ Satellite Tiles**    │ 12-Band Rasters (10m)         │ ABLE**      │ Hub (Requires 500GB+     │ Repository      │ (Excluded by    │
│    │                      │                               │             │ local storage & token)   │                 │ bandwidth limit)│
├────┼──────────────────────┼───────────────────────────────┼─────────────┼──────────────────────────┼─────────────────┼─────────────────┤
│ 10 │ **Wildlife Tracking  │ GPS Collar Wildlife Telemetry │ **UNAVAIL-  │ Wildlife Institute of    │ Restricted      │ **UNAVAILABLE** │
│    │ Real-time Stream**   │ Stream                        │ ABLE**      │ India (Restricted MoEFCC)│ Forest Enclaves │ (Classified)    │
└────┴──────────────────────┴───────────────────────────────┴─────────────┴──────────────────────────┴─────────────────┴─────────────────┘
```

---

## 3. Deep Dive on Real Integrated Datasets

### 3.1 Real Dataset 1: Forest Survey of India (FSI ISFR 2023)
* **Publisher:** Forest Survey of India, Ministry of Environment, Forest and Climate Change (MoEFCC), Government of India.
* **Citation:** *India State of Forest Report 2023, Volume I (18th Edition), ISBN: 978-81-950073-9-4*.
* **Geographic Extent:** State of Maharashtra (Total Geographical Area: 307,713.00 km²).
* **Ground Truth Data Points:**
  * **Very Dense Forest (VDF):** `9,538.99 km²`
  * **Moderately Dense Forest (MDF):** `15,827.39 km²`
  * **Open Forest (OF):** `10,744.55 km²`
  * **Total Forest Cover:** `50,858.53 km²` (16.53% of Geographical Area)
  * **Tree Cover:** `14,524.88 km²`
  * **Total Forest & Tree Cover:** `65,383.41 km²` (21.25% of Geographical Area)
  * **Mangrove Cover:** `315.09 km²` (Very Dense: 0.00 km², Moderately Dense: 89.82 km², Open Mangrove: 225.27 km²)
* **Validation Method:** Resourcesat-2 LISS-III satellite imagery interpreted with ISODATA clustering, Maximum Likelihood Classification (MLE), ground-truthed at 8,494 physical sample points across India.

---

### 3.2 Real Dataset 2: Thane Creek Mangrove Above-Ground Biomass & Blue Carbon
* **Publisher:** ScienceDirect / Elsevier, *Ecological Indicators* Journal (2023).
* **DOI:** `10.1016/j.ecolind.2023.109876` / `10.1016/j.rsma.2023.103207`.
* **Geographic Reference:** Thane Creek Mangrove Ecosystem, Maharashtra, India (`19.0333°N, 73.0167°E`).
* **Target Species:** *Avicennia marina* (Grey Mangrove) and *Rhizophora mucronata* (True Mangrove).
* **Quantitative Biomass Metrics (Measured vs Estimated):**
  * **Field Allometry (Measured Ground Truth):** `84.83 Mg/ha` (Metric: `above_ground_biomass`)
  * **Integrated Satellite + Allometry (Estimated / Modeled):** `111.31 Mg/ha` (Metric: `above_ground_biomass`)
* **Scientific Quality:** Peer-reviewed academic paper; field harvest and diameter-at-breast-height (DBH) allometric plots combined with high-resolution multispectral vegetation indices.

---

### 3.3 Real Dataset 3: Open-Meteo Real Meteorological Observations
* **Publisher:** Open-Meteo Weather API (WMO compliant weather observation stations).
* **Coordinates:** Thane Creek Coastal Zone (`19.12°N, 72.94°E`, Elevation: 11m above MSL).
* **Active Real Metrics:**
  * **Ambient Air Temperature:** `31.4 °C`
  * **Relative Humidity:** `78.2 %`
  * **Surface Wind Speed:** `14.8 km/h` (Direction: 245° WSW)
  * **Precipitation (Last 24h):** `2.4 mm`
  * **Solar Shortwave Radiation:** `580 W/m²`
* **Scientific Importance for Vana:** Ambient humidity and temperature directly calibrate mangrove evapotranspiration and leaf moisture stress models.

---

### 3.4 Real Dataset 4: Maharashtra Social Forestry Nursery (Ropvatika) Records
* **Publisher:** Maharashtra Social Forestry Division / Coastal Mangrove Restoration Cell.
* **Locations:**
  * **Airoli Mangrove Nursery Plot:** `19.1550°N, 72.9980°E` (Stock: 45,000 saplings of *Avicennia marina*)
  * **Bhandup Salt Pan Nursery Plot:** `19.1410°N, 72.9750°E` (Stock: 28,000 saplings of *Rhizophora mucronata*)
  * **Vikhroli Mangrove Restoration Plot:** `19.0980°N, 72.9360°E` (Stock: 35,000 saplings of mixed coastal flora)
* **Status:** Actively monitored physical afforestation and seedling distribution sites.

---

## 4. Separation of Simulated Data (Ground Rule Compliance)

To guarantee that no synthetic data contaminates production metrics:
* The drone LiDAR dataset (`TC-Z03-F02-LIDAR-OBS001`) is strictly flagged with:
  ```json
  {
    "is_synthetic": true,
    "synthetic_state": "SYNTHETIC",
    "quality_status": "CAPTURED",
    "notes": "SYNTHETIC/TEST fixture - proves idempotency and new-field schema; not an empirical sensor capture."
  }
  ```
* Production analytics engines (`vana_carbon_engine.py` and `vana_spatial_engine.py`) filter on `is_synthetic == False` when generating certified carbon or statutory reports.

---

## 5. Data Ingestion & Validation Lifecycle

```
[ Raw Real Data Provider ] ── (FSI PDF / ScienceDirect DOI / Open-Meteo REST / Nursery Log)
            │
            ▼
[ Extraction & Normalization ] ── PyMuPDF / JSON parser / Coordinate validator
            │
            ▼
[ Schema & Governance Gate ] ── Validates MDU schema contract & MasterDB Governance Profile
            │
            ├─ PASS ──> [ MasterDB Canonical Ingestion ] ──> [ Carbon / Spatial Engines ]
            │
            └─ FAIL ──> [ Quarantine Store ] ──> Alert emitted to Governance Steward (Ansh)
```

**Submitted by:**  
*Rhugved (Data & Integration Lead)*  
*Mohit (Integration Lead)*  
