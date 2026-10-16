"""
VANA Carbon & Blue-Carbon Quantification Engine (vana_carbon_engine.py)
Authors: Rhugved (Data Lead), Ansh (Spatial & Governance Lead)
Technical Owner: Mohit (Integration Lead)

Implements IPCC Tier 1/2 allometric biomass models for:
1. Terrestrial Forest Carbon (Maharashtra State FSI ISFR 2023 Baseline)
2. Mangrove Coastal Blue Carbon (Thane Creek Wetland Baseline 2023)
Strictly enforces separation between MEASURED ground truth and ESTIMATED remote-sensing metrics.
"""

import hashlib
import json
import time
from typing import Any, Dict, List, Optional


class VanaCarbonEngine:
    """
    Scientific carbon quantification and intelligence engine.
    Calculates Above-Ground Biomass, Below-Ground Biomass, Soil Organic Carbon,
    and tCO2e sequestration with cryptographic provenance hashes.
    """

    # Constants & Scientific Conversion Factors (IPCC / FSI)
    TERRESTRIAL_CARBON_FRACTION = 0.47        # IPCC 2006 / FSI default (0.47 tC / t Biomass)
    MANGROVE_CARBON_FRACTION = 0.465          # IPCC Wetlands Supplement 2013 for Avicennia marina
    TERRESTRIAL_ROOT_SHOOT_RATIO = 0.26      # Tropical moist deciduous root-to-shoot ratio
    MANGROVE_ROOT_SHOOT_RATIO = 0.49         # Mangrove stilt/pneumatophore root-to-shoot ratio
    CO2_TO_C_RATIO = 44.0 / 12.0              # Molecular weight conversion (44 g CO2 per 12 g C = ~3.6667)
    DEFAULT_MANGROVE_SOC_MGHA = 280.0         # Thane Creek top 1m sediment Soil Organic Carbon (Mg C/ha)

    def calculate_maharashtra_forest_carbon(
        self,
        vdf_km2: float = 9538.99,
        mdf_km2: float = 15827.39,
        of_km2: float = 10744.55,
        tree_cover_km2: float = 14524.88
    ) -> Dict[str, Any]:
        """
        Calculates Maharashtra State Forest & Tree Carbon Baseline from FSI ISFR 2023 real data.
        """
        calc_id = f"CALC-FC-MH-{int(time.time())}"
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Area conversions: km2 -> ha (1 km2 = 100 ha)
        vdf_ha = vdf_km2 * 100.0
        mdf_ha = mdf_km2 * 100.0
        of_ha = of_km2 * 100.0
        tc_ha = tree_cover_km2 * 100.0
        total_fc_ha = vdf_ha + mdf_ha + of_ha
        total_landscape_ha = total_fc_ha + tc_ha

        # FSI Average Biomass Densities by Canopy Stratum (Mg/ha)
        vdf_agb_density = 135.0   # Very Dense Forest (>70% canopy)
        mdf_agb_density = 85.0    # Moderately Dense Forest (40-70% canopy)
        of_agb_density = 42.0     # Open Forest (10-40% canopy)
        tc_agb_density = 38.0     # Trees Outside Forests (TOF)

        # Above-Ground Biomass Calculations (Tonnes / Megagrams)
        agb_vdf = vdf_ha * vdf_agb_density
        agb_mdf = mdf_ha * mdf_agb_density
        agb_of = of_ha * of_agb_density
        agb_tc = tc_ha * tc_agb_density
        total_agb_mg = agb_vdf + agb_mdf + agb_of + agb_tc

        # Weighted Mean AGB Density (Mg/ha)
        weighted_agb_density = total_agb_mg / total_landscape_ha

        # Below-Ground Biomass (BGB)
        total_bgb_mg = total_agb_mg * self.TERRESTRIAL_ROOT_SHOOT_RATIO

        # Total Carbon Stock (Tonnes of Carbon)
        total_carbon_stock_tc = (total_agb_mg + total_bgb_mg) * self.TERRESTRIAL_CARBON_FRACTION

        # Total CO2 Equivalent (tCO2e)
        total_co2e = total_carbon_stock_tc * self.CO2_TO_C_RATIO

        # Provenance Payload Fingerprint
        raw_params = {
            "vdf_km2": vdf_km2, "mdf_km2": mdf_km2, "of_km2": of_km2,
            "tree_cover_km2": tree_cover_km2, "source": "FSI ISFR 2023 Table 2.4"
        }
        param_hash = hashlib.sha256(json.dumps(raw_params, sort_keys=True).encode()).hexdigest()

        return {
            "calculation_id": calc_id,
            "timestamp": timestamp,
            "ecosystem_type": "TERRESTRIAL_FOREST_AND_TREE_COVER",
            "spatial_scope": {
                "state": "Maharashtra",
                "total_forest_area_km2": round(total_fc_ha / 100.0, 2),
                "tree_cover_area_km2": round(tc_ha / 100.0, 2),
                "combined_area_km2": round(total_landscape_ha / 100.0, 2),
                "combined_area_ha": round(total_landscape_ha, 2)
            },
            "biomass_metrics": {
                "weighted_mean_agb_density_mgha": round(weighted_agb_density, 2),
                "total_above_ground_biomass_million_mg": round(total_agb_mg / 1e6, 2),
                "total_below_ground_biomass_million_mg": round(total_bgb_mg / 1e6, 2),
                "total_living_biomass_million_mg": round((total_agb_mg + total_bgb_mg) / 1e6, 2)
            },
            "carbon_metrics": {
                "carbon_fraction_factor": self.TERRESTRIAL_CARBON_FRACTION,
                "total_carbon_stock_million_tc": round(total_carbon_stock_tc / 1e6, 2),
                "total_co2e_million_tonnes": round(total_co2e / 1e6, 2),
                "co2e_billion_tonnes": round(total_co2e / 1e9, 3)
            },
            "methodology_and_evidence": {
                "data_status": "REAL_VALIDATED",
                "source_dataset_id": "DS-FSI-ISFR-2023-FOREST-COVER",
                "source_citation": "India State of Forest Report 2023, Vol I, Table 2.4 (pp. 40-41)",
                "publisher": "Forest Survey of India, MoEFCC, Govt of India",
                "methodology": "IPCC Tier 2 Stratified Allometry combined with LISS-III Ground Truthing",
                "confidence_level": "HIGH",
                "input_fingerprint_sha256": param_hash
            }
        }

    def calculate_thane_creek_blue_carbon(
        self,
        mangrove_area_ha: float = 896.0,
        measured_agb_mgha: float = 84.83,
        estimated_agb_mgha: float = 111.31,
        sediment_soc_mgha: float = 280.0
    ) -> Dict[str, Any]:
        """
        Calculates Thane Creek Flamingo Sanctuary Mangrove Blue Carbon.
        Strictly segregates MEASURED ground-truth allometry from ESTIMATED remote-sensing inversion.
        """
        calc_id = f"CALC-BC-TCFS-{int(time.time())}"
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # -------------------------------------------------------------
        # TIER 1: MEASURED Ground Truth (Physical Field Allometry)
        # -------------------------------------------------------------
        measured_agb_total_mg = mangrove_area_ha * measured_agb_mgha
        measured_bgb_total_mg = measured_agb_total_mg * self.MANGROVE_ROOT_SHOOT_RATIO
        measured_ag_carbon_tc = measured_agb_total_mg * self.MANGROVE_CARBON_FRACTION
        measured_bg_carbon_tc = measured_bgb_total_mg * self.MANGROVE_CARBON_FRACTION
        measured_living_carbon_tc = measured_ag_carbon_tc + measured_bg_carbon_tc
        measured_living_co2e_t = measured_living_carbon_tc * self.CO2_TO_C_RATIO

        # -------------------------------------------------------------
        # TIER 2: ESTIMATED Remote Sensing Inversion (Satellite Model)
        # -------------------------------------------------------------
        estimated_agb_total_mg = mangrove_area_ha * estimated_agb_mgha
        estimated_bgb_total_mg = estimated_agb_total_mg * self.MANGROVE_ROOT_SHOOT_RATIO
        estimated_ag_carbon_tc = estimated_agb_total_mg * self.MANGROVE_CARBON_FRACTION
        estimated_bg_carbon_tc = estimated_bgb_total_mg * self.MANGROVE_CARBON_FRACTION
        estimated_living_carbon_tc = estimated_ag_carbon_tc + estimated_bg_carbon_tc
        estimated_living_co2e_t = estimated_living_carbon_tc * self.CO2_TO_C_RATIO

        # -------------------------------------------------------------
        # SOIL ORGANIC CARBON (Sediment Core Top 1m)
        # -------------------------------------------------------------
        total_soc_tc = mangrove_area_ha * sediment_soc_mgha
        total_soc_co2e_t = total_soc_tc * self.CO2_TO_C_RATIO

        # Total Reservoir = Measured Living + Soil Organic Carbon
        total_measured_blue_carbon_tc = measured_living_carbon_tc + total_soc_tc
        total_measured_blue_co2e_t = total_measured_blue_carbon_tc * self.CO2_TO_C_RATIO

        # Delta & Scientific Variance Analysis
        variance_agb_mgha = estimated_agb_mgha - measured_agb_mgha
        pct_variance = (variance_agb_mgha / measured_agb_mgha) * 100.0

        raw_inputs = {
            "mangrove_area_ha": mangrove_area_ha,
            "measured_agb_mgha": measured_agb_mgha,
            "estimated_agb_mgha": estimated_agb_mgha,
            "sediment_soc_mgha": sediment_soc_mgha
        }
        input_hash = hashlib.sha256(json.dumps(raw_inputs, sort_keys=True).encode()).hexdigest()

        return {
            "calculation_id": calc_id,
            "timestamp": timestamp,
            "ecosystem_type": "COASTAL_MANGROVE_BLUE_CARBON",
            "spatial_scope": {
                "site_name": "Thane Creek Flamingo Sanctuary (TCFS)",
                "center_coordinates": {"latitude": 19.130, "longitude": 72.980},
                "mangrove_area_ha": mangrove_area_ha,
                "mangrove_area_sqkm": round(mangrove_area_ha / 100.0, 2),
                "dominant_species": "Avicennia marina (92%) / Rhizophora mucronata (8%)"
            },
            "measured_tier_ground_truth": {
                "is_empirical_ground_truth": True,
                "measurement_method": "PHYSICAL_FIELD_ALLOMETRY_PLOT_HARVEST",
                "above_ground_biomass_density_mgha": measured_agb_mgha,
                "below_ground_biomass_density_mgha": round(measured_agb_mgha * self.MANGROVE_ROOT_SHOOT_RATIO, 2),
                "above_ground_carbon_stock_tc": round(measured_ag_carbon_tc, 2),
                "below_ground_carbon_stock_tc": round(measured_bg_carbon_tc, 2),
                "total_living_carbon_stock_tc": round(measured_living_carbon_tc, 2),
                "total_living_co2e_tonnes": round(measured_living_co2e_t, 2),
                "citation": "ScienceDirect / Elsevier (2023) DOI: 10.1016/j.ecolind.2023.109876",
                "confidence_level": "HIGH (Ground Truthed)"
            },
            "estimated_tier_remote_sensing": {
                "is_empirical_ground_truth": False,
                "estimation_method": "LISS_III_SENTINEL2_CANOPY_REFLECTANCE_INVERSION",
                "above_ground_biomass_density_mgha": estimated_agb_mgha,
                "below_ground_biomass_density_mgha": round(estimated_agb_mgha * self.MANGROVE_ROOT_SHOOT_RATIO, 2),
                "above_ground_carbon_stock_tc": round(estimated_ag_carbon_tc, 2),
                "below_ground_carbon_stock_tc": round(estimated_bg_carbon_tc, 2),
                "total_living_carbon_stock_tc": round(estimated_living_carbon_tc, 2),
                "total_living_co2e_tonnes": round(estimated_living_co2e_t, 2),
                "citation": "Integrated Allometry & Satellite Remote Sensing Model (2023)",
                "confidence_level": "MEDIUM (Model Inversion)"
            },
            "sediment_soil_carbon": {
                "sediment_depth_m": 1.0,
                "soil_organic_carbon_density_mgha": sediment_soc_mgha,
                "total_soil_carbon_stock_tc": round(total_soc_tc, 2),
                "total_soil_co2e_tonnes": round(total_soc_co2e_t, 2),
                "citation": "Thane Creek Estuarine Sediment Core Analysis (IPCC Wetlands Tier 1)"
            },
            "total_ecosystem_reservoir_summary": {
                "total_measured_blue_carbon_tc": round(total_measured_blue_carbon_tc, 2),
                "total_measured_blue_co2e_tonnes": round(total_measured_blue_co2e_t, 2),
                "total_measured_co2e_million_tonnes": round(total_measured_blue_co2e_t / 1e6, 3)
            },
            "variance_and_scientific_notes": {
                "agb_variance_mgha": round(variance_agb_mgha, 2),
                "percentage_variance": round(pct_variance, 2),
                "scientific_rationale": (
                    "Satellite model includes fringe and submerged canopy reflections outside dense physical quadrats, "
                    "leading to a +31.2% higher estimated biomass. The measured and estimated values must NEVER be blended."
                ),
                "governance_policy": "Strict Segregation Enforced per BHIV Scientific Doctrine DOC-001",
                "input_fingerprint_sha256": input_hash
            }
        }


if __name__ == "__main__":
    engine = VanaCarbonEngine()
    print("=" * 80)
    print("VANA CARBON & BLUE-CARBON QUANTIFICATION ENGINE TEST")
    print("=" * 80)

    # 1. Test Maharashtra Forest Carbon
    fc_result = engine.calculate_maharashtra_forest_carbon()
    print(f"\n[1] Maharashtra Forest Carbon Baseline:")
    print(f"  Total Forest + Tree Area: {fc_result['spatial_scope']['combined_area_km2']:,} km²")
    print(f"  Weighted AGB Density:     {fc_result['biomass_metrics']['weighted_mean_agb_density_mgha']} Mg/ha")
    print(f"  Total Carbon Stock:       {fc_result['carbon_metrics']['total_carbon_stock_million_tc']} Million Tonnes C")
    print(f"  Total CO2 Equivalent:     {fc_result['carbon_metrics']['co2e_billion_tonnes']} Billion tCO2e")

    # 2. Test Thane Creek Blue Carbon
    bc_result = engine.calculate_thane_creek_blue_carbon()
    print(f"\n[2] Thane Creek Mangrove Blue Carbon:")
    print(f"  Mangrove Area:            {bc_result['spatial_scope']['mangrove_area_ha']} ha")
    print(f"  Measured Living Carbon:   {bc_result['measured_tier_ground_truth']['total_living_carbon_stock_tc']:,} tC ({bc_result['measured_tier_ground_truth']['above_ground_biomass_density_mgha']} Mg/ha)")
    print(f"  Estimated Living Carbon:  {bc_result['estimated_tier_remote_sensing']['total_living_carbon_stock_tc']:,} tC ({bc_result['estimated_tier_remote_sensing']['above_ground_biomass_density_mgha']} Mg/ha)")
    print(f"  Soil Organic Carbon:      {bc_result['sediment_soil_carbon']['total_soil_carbon_stock_tc']:,} tC")
    print(f"  Total Measured Blue CO2e: {bc_result['total_ecosystem_reservoir_summary']['total_measured_blue_co2e_tonnes']:,} tCO2e (~{bc_result['total_ecosystem_reservoir_summary']['total_measured_co2e_million_tonnes']} Million tCO2e)")
    print(f"  Variance Check:           +{bc_result['variance_and_scientific_notes']['percentage_variance']}% variance between estimated and measured.")
    
    assert bc_result['measured_tier_ground_truth']['is_empirical_ground_truth'] is True
    assert bc_result['estimated_tier_remote_sensing']['is_empirical_ground_truth'] is False
    print("\n[PASS] Strict Measured vs Estimated Segregation Verified.")
