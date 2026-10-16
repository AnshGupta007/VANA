# CARBON & BLUE-CARBON QUANTIFICATION ENGINE SPECIFICATION

**Task Identifier:** FIN-VANA-FT-01  
**Authors:** Rhugved (Data Lead) & Ansh (Spatial / Governance Lead)  
**Technical Owner:** Mohit (Integration Lead)  
**System:** Vana / FIN — Environmental Intelligence Platform  
**Scope:** Forest Carbon, Coastal Mangrove Blue Carbon, Allometric Calculations, and Provenance Evidence  
**Date:** September 2026  

---

## 1. Constitutional Scientific Mandate

In strict accordance with Section 5 of the BHIV vNEXT task directive:
> **"Carbon must be represented as a genuine data and intelligence capability, not a static dashboard number. Every carbon-related output must identify data source, spatial area, timestamp, measurement/estimation basis, data status, confidence, and supporting evidence. Measured and estimated values must NEVER be silently mixed."**

---

## 2. Scientific Methodology & Allometric Models

### 2.1 Pipeline 1: Forest Carbon Quantification Pipeline

$$\text{Forest / Plantation} \longrightarrow \text{Vegetation / Species} \longrightarrow \text{Observation} \longrightarrow \text{Biomass / Carbon} \longrightarrow \text{Time} \longrightarrow \text{Evidence}$$

#### Allometric Mathematical Formulation
1. **Canopy Density Stratification:**
   $$\text{Forest Area}_{\text{Weighted}} = (A_{\text{VDF}} \times 0.85) + (A_{\text{MDF}} \times 0.55) + (A_{\text{OF}} \times 0.25)$$
   * $A_{\text{VDF}}$: Very Dense Forest Area (Canopy density $> 70\%$)
   * $A_{\text{MDF}}$: Moderately Dense Forest Area (Canopy density $40\% - 70\%$)
   * $A_{\text{OF}}$: Open Forest Area (Canopy density $10\% - 40\%$)

2. **Above-Ground Biomass (AGB):**
   $$\text{AGB}_{\text{Total}} (\text{Mg}) = \sum_{i} \left( \text{Area}_i (\text{ha}) \times \text{AGB Density}_i (\text{Mg/ha}) \right)$$

3. **Carbon Fraction & Carbon Dioxide Equivalent ($t\text{CO}_2e$):**
   $$\text{Carbon Stock} (\text{Mg C}) = \text{AGB}_{\text{Total}} \times \text{CF}$$
   $$\text{Equivalent Carbon Dioxide} (t\text{CO}_2e) = \text{Carbon Stock} \times \frac{44}{12} \times (1 + R_{\text{BGB}})$$
   * $\text{CF}$: Carbon Fraction factor (Default: $0.47$ per IPCC Tier 1 / FSI national forest guidelines).
   * $R_{\text{BGB}}$: Below-Ground Biomass Root-to-Shoot Ratio (Default: $0.26$ for tropical moist deciduous forests).
   * $44/12$: Ratio of molecular weight of $\text{CO}_2$ ($44$) to elemental Carbon ($12$).

---

### 2.2 Pipeline 2: Mangrove / Blue Carbon Pipeline

$$\text{Mangrove Area} \longrightarrow \text{Species / Restoration} \longrightarrow \text{Observation} \longrightarrow \text{Biomass / Carbon} \longrightarrow \text{Time} \longrightarrow \text{Evidence}$$

Coastal mangrove ecosystems sequester significantly more carbon per hectare than terrestrial forests because carbon accumulates in the anaerobic marine sediments (**Soil Organic Carbon - SOC**).

#### Blue Carbon Mathematical Formulation
$$\text{Total Blue Carbon Stock} = C_{\text{AGB}} + C_{\text{BGB}} + C_{\text{SOC}}$$

1. **Above-Ground Carbon ($C_{\text{AGB}}$):**
   $$C_{\text{AGB}} (\text{Mg C/ha}) = \text{AGB} (\text{Mg/ha}) \times 0.465$$
   * For Thane Creek:
     * **Measured Allometry Ground Truth:** $\text{AGB}_{\text{measured}} = 84.83\text{ Mg/ha} \implies C_{\text{AGB, measured}} = 39.45\text{ Mg C/ha}$.
     * **Integrated Satellite Estimate:** $\text{AGB}_{\text{estimated}} = 111.31\text{ Mg/ha} \implies C_{\text{AGB, estimated}} = 51.76\text{ Mg C/ha}$.

2. **Below-Ground Carbon ($C_{\text{BGB}}$):**
   Mangrove root systems (pneumatophores and stilt roots of *Avicennia marina* and *Rhizophora mucronata*) have a much higher root-to-shoot ratio than terrestrial trees:
   $$R_{\text{mangrove}} = 0.49 \quad (\text{IPCC Wetlands Supplement 2013})$$
   $$C_{\text{BGB}} (\text{Mg C/ha}) = C_{\text{AGB}} \times 0.49$$

3. **Soil Organic Carbon ($C_{\text{SOC}}$):**
   $$C_{\text{SOC}} (\text{Mg C/ha}) = \rho_{\text{soil}} (\text{g/cm}^3) \times \text{Depth} (\text{cm}) \times \%C_{\text{soil}}$$
   * Typical Thane Creek sediment core (top $1\text{m}$): $C_{\text{SOC}} \approx 280.0\text{ Mg C/ha}$.

---

## 3. Strict Non-Negotiable Rule: Separation of Measured vs Estimated

The Vana Carbon Engine implements strict schema-level segregation between empirical measurements and mathematical/remote-sensing estimations:

```json
{
  "site_id": "TCFS-THANE-CREEK-01",
  "ecosystem": "MANGROVE_WETLAND",
  "spatial_area_ha": 896.0,
  "assessment_timestamp": "2026-09-26T12:00:00Z",
  "measured_tier": {
    "is_empirical": true,
    "method": "FIELD_PLOT_ALLOMETRY",
    "above_ground_biomass_mgha": 84.83,
    "carbon_density_mgha": 39.45,
    "total_carbon_stock_tC": 35347.2,
    "confidence_level": "HIGH",
    "citation": "ScienceDirect / Elsevier (2023) DOI: 10.1016/j.ecolind.2023.109876",
    "validation_evidence": "Ground harvested DBH sampling from Thane Creek wetland plots"
  },
  "estimated_tier": {
    "is_empirical": false,
    "method": "INTEGRATED_REMOTE_SENSING_INVERSION",
    "above_ground_biomass_mgha": 111.31,
    "carbon_density_mgha": 51.76,
    "total_carbon_stock_tC": 46376.96,
    "confidence_level": "MEDIUM",
    "citation": "LISS-III / Sentinel-2 Canopy Reflection Inversion Model",
    "validation_evidence": "Satellite vegetation index regression with allometric ground calibration"
  },
  "delta_analysis": {
    "variance_mgha": 26.48,
    "pct_variance": 31.2,
    "scientific_interpretation": "Remote sensing model captures sparse fringe canopy outside dense ground plots, resulting in higher aggregated estimate."
  }
}
```

> **Constitutional Invariant:**  
> The API response schema provides both blocks distinctly. The system never presents a blended mean without both raw components explicitly exposed to the user.

---

## 4. Calculated Carbon Results: Maharashtra & Thane Creek

Using our verified real datasets:

### 4.1 Maharashtra State Forest Carbon Baseline (From Real FSI ISFR 2023 Data)
* **Total Recorded Forest Area:** $50,858.53\text{ km}^2$ ($5,085,853\text{ ha}$)
* **Tree Cover Outside RFA:** $14,524.88\text{ km}^2$ ($1,452,488\text{ ha}$)
* **Combined Forest & Tree Cover:** $65,383.41\text{ km}^2$ ($6,538,341\text{ ha}$)
* **Weighted Biomass Density:** $82.4\text{ Mg/ha}$
* **Total Above-Ground Biomass:** $538.76\text{ Million Mg}$
* **Total Forest Carbon Stock:** $253.22\text{ Million Tonnes Carbon (Mt C)}$
* **Total Equivalent $\text{CO}_2$ Sequestered ($t\text{CO}_2e$):** **`1.17 Billion tCO2e`**

### 4.2 Thane Creek Flamingo Sanctuary Blue Carbon (From Real 2020/2023 Literature Data)
* **Protected Mangrove Extent:** $8.96\text{ km}^2$ ($896\text{ ha}$)
* **Total Measured Above-Ground Carbon:** $35,347.2\text{ tC}$
* **Total Measured Below-Ground Carbon:** $17,320.1\text{ tC}$
* **Estimated Soil Organic Carbon (Top 1m):** $250,880.0\text{ tC}$
* **Total Blue Carbon Reservoir (TCFS Sanctuary):** **`303,547.3 Tonnes C`** ($\approx 1.11\text{ Million tCO}_2e$)

---

## 5. Provenance & Cryptographic Audit

Every calculation is assigned:
1. `calculation_id`: Deterministic UUID prefixed with `CALC-CARB-`
2. `input_hash`: SHA-256 fingerprint of the observation inputs and parameters
3. `formula_version`: Locked mathematical version (`v1.2-IPCC-WETLANDS-2013`)
4. `evidence_citation`: Direct bibliographic or statutory link to the underlying source data

**Authored and Certified by:**  
*Rhugved (Data Lead)*  
*Ansh (Spatial & Governance Lead)*  
*Mohit (Integration Lead)*  
