"""
Unit Tests for VANA Local LLM Client (Deterministic AI Verification)
===================================================================
Task ID: T-GOV-F01
Assignee: Ansh Gupta
"""

import pytest
from integrations.local_llm_client import LocalLLMClient, LLMVerificationResponse


@pytest.mark.unit
class TestLocalLLMClient:
    """Test suite for LocalLLMClient offline-safe deterministic verification."""

    def test_verify_forest_carbon_valid(self, local_llm):
        """Verify normal forest carbon density passes verification."""
        resp = local_llm.verify_environmental_claim(
            claim_type="forest_carbon",
            parameters={"carbon_density_mgha": 55.4},
            provenance_source="DS-FSI-ISFR-2023-FOREST-COVER"
        )
        assert isinstance(resp, LLMVerificationResponse)
        assert resp.verified is True
        assert resp.confidence == 0.98
        assert len(resp.detected_anomalies) == 0
        assert resp.deterministic_hash is not None

    def test_verify_forest_carbon_out_of_bounds(self, local_llm):
        """Verify implausible carbon density is flagged."""
        resp = local_llm.verify_environmental_claim(
            claim_type="forest_carbon",
            parameters={"carbon_density_mgha": 999.0},  # Exceeds 350
            provenance_source="DS-FSI-ISFR-2023-FOREST-COVER"
        )
        assert resp.verified is False
        assert resp.confidence == 0.40
        assert any("exceeds physiological limits" in a for a in resp.detected_anomalies)

    def test_verify_mangrove_blue_carbon_valid_variance(self, local_llm):
        """Verify acceptable satellite-to-ground variance (<60%) passes."""
        resp = local_llm.verify_environmental_claim(
            claim_type="mangrove_blue_carbon",
            parameters={"measured_agb": 84.83, "estimated_agb": 111.31},  # ~31% variance
            provenance_source="DS-THANECREEK-2023-BIOMASS"
        )
        assert resp.verified is True
        assert resp.confidence == 0.98
        assert len(resp.detected_anomalies) == 0

    def test_verify_mangrove_blue_carbon_excessive_variance(self, local_llm):
        """Verify excessive variance (>60%) is flagged as anomaly."""
        resp = local_llm.verify_environmental_claim(
            claim_type="mangrove_blue_carbon",
            parameters={"measured_agb": 50.0, "estimated_agb": 150.0},  # 200% variance
            provenance_source="DS-THANECREEK-2023-BIOMASS"
        )
        assert resp.verified is False
        assert any("exceeds acceptable calibration threshold" in a for a in resp.detected_anomalies)

    def test_verify_mangrove_blue_carbon_negative_values(self, local_llm):
        """Verify negative biomass density is flagged."""
        resp = local_llm.verify_environmental_claim(
            claim_type="mangrove_blue_carbon",
            parameters={"measured_agb": -10.0, "estimated_agb": 50.0},
            provenance_source="DS-THANECREEK-2023-BIOMASS"
        )
        assert resp.verified is False
        assert any("strictly positive" in a for a in resp.detected_anomalies)

    def test_verify_synthetic_source_flagged(self, local_llm):
        """Verify synthetic / mock source names are automatically flagged."""
        resp = local_llm.verify_environmental_claim(
            claim_type="forest_carbon",
            parameters={"carbon_density_mgha": 55.4},
            provenance_source="MOCK_SYNTHETIC_TEST_FIXTURE_001"
        )
        assert resp.verified is False
        assert any("indicates non-canonical synthetic data" in a for a in resp.detected_anomalies)

    def test_determinism_hashes_identical(self, local_llm):
        """Verify two identical requests produce identical deterministic hashes."""
        resp1 = local_llm.verify_environmental_claim(
            claim_type="forest_carbon",
            parameters={"carbon_density_mgha": 60.0},
            provenance_source="DS-FSI-ISFR-2023-FOREST-COVER"
        )
        resp2 = local_llm.verify_environmental_claim(
            claim_type="forest_carbon",
            parameters={"carbon_density_mgha": 60.0},
            provenance_source="DS-FSI-ISFR-2023-FOREST-COVER"
        )
        assert resp1.deterministic_hash == resp2.deterministic_hash
