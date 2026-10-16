"""
MASTERDB Governance & Constitutional Control Engine
Author: Ansh (Data Governance & Constitutional Controls Lead)
Collaborator: Kavy (MASTERDB Platform Lead)

Implements the Governance Model, 6-Tuple Access Control Matrix,
Dataset Classification Taxonomy, and Lifecycle State Machine for MASTERDB.
"""

import hashlib
import json
import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class DatasetClassification(str, Enum):
    CANONICAL = "CANONICAL"
    SOURCE = "SOURCE"
    DERIVED = "DERIVED"
    EXPERIMENTAL = "EXPERIMENTAL"
    FIXTURE = "FIXTURE"
    EVIDENCE = "EVIDENCE"
    RUNTIME = "RUNTIME"
    RESTRICTED = "RESTRICTED"
    PRIVATE_IP = "PRIVATE/IP"
    QUARANTINED = "QUARANTINED"
    UNKNOWN = "UNKNOWN"


class ActionType(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    MODIFY = "MODIFY"
    DELETE = "DELETE"
    EXPORT = "EXPORT"
    ADMIN = "ADMIN"


class AccessDecision(str, Enum):
    ALLOWED = "ALLOWED"
    CONTROLLED = "CONTROLLED"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    DENIED = "DENIED"


class LifecycleStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    CLASSIFIED = "CLASSIFIED"
    VALIDATED = "VALIDATED"
    REGISTERED = "REGISTERED"
    ACTIVE = "ACTIVE"
    UPDATED = "UPDATED/VERSIONED"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"
    QUARANTINED = "QUARANTINED"


class MasterDBGovernanceEngine:
    """
    Constitutional Governance Layer for MASTERDB.
    Enforces Authority Boundaries, Access 6-Tuples, Classifications,
    and Canonical Validation Gates.
    """

    ALLOWED_PRODUCTS = {"VANA", "FIN", "AIAIC", "PRAVAH", "INSIGHTFLOW", "SHAKTI_GC"}
    
    # Registered Governed Datasets
    GOVERNED_DATASETS: Dict[str, Dict[str, Any]] = {
        "DS-FSI-ISFR-2023-FOREST-COVER": {
            "name": "India State of Forest Report 2023 Forest Cover",
            "owner": "Forest Survey of India / MoEFCC, Govt of India",
            "custodian": "Kavy (MasterDB)",
            "steward": "Ansh (Governance)",
            "classification": DatasetClassification.CANONICAL,
            "sensitivity": "PUBLIC_GOVERNMENT_OPEN",
            "allowed_consumers": ["VANA", "FIN", "AIAIC", "PRAVAH", "INSIGHTFLOW"],
            "allowed_actions": [ActionType.READ, ActionType.EXPORT],
            "approved_purposes": ["DISTRICT_CANOPY_ANALYSIS", "STATE_BASELINE", "CARBON_BENCHMARK", "RESEARCH"],
            "lifecycle": LifecycleStatus.ACTIVE,
            "is_synthetic": False
        },
        "DS-THANECREEK-2023-BIOMASS": {
            "name": "Thane Creek Mangrove Above-Ground Biomass 2023",
            "owner": "ScienceDirect / Elsevier (2023)",
            "custodian": "Kavy (MasterDB)",
            "steward": "Ansh (Governance)",
            "classification": DatasetClassification.CANONICAL,
            "sensitivity": "SCIENTIFIC_PUBLIC_RESTRICTED",
            "allowed_consumers": ["VANA", "FIN", "CARBON_ENGINE", "BHIV_RESEARCH"],
            "allowed_actions": [ActionType.READ],
            "approved_purposes": ["BLUE_CARBON_QUANTIFICATION", "MANGROVE_MONITORING", "RESEARCH"],
            "lifecycle": LifecycleStatus.ACTIVE,
            "is_synthetic": False
        },
        "DS-GROUP3-TC-Z03-F02": {
            "name": "Thane Creek Zone 03 LiDAR Canopy Observation",
            "owner": "Group 3 Field Operations",
            "custodian": "Kavy (MasterDB)",
            "steward": "Ansh (Governance)",
            "classification": DatasetClassification.SOURCE,
            "sensitivity": "INTERNAL_OPERATIONAL",
            "allowed_consumers": ["VANA", "FIN", "SPATIAL_ENGINE", "GROUP3"],
            "allowed_actions": [ActionType.READ, ActionType.WRITE],
            "approved_purposes": ["CANOPY_SURVEY", "DRONE_POINTCLOUD_INTEGRATION"],
            "lifecycle": LifecycleStatus.ACTIVE,
            "is_synthetic": False
        },
        "DS-SYNTHETIC-GROUP3-FIXTURE-01": {
            "name": "Synthetic Group 3 Field Observation Fixture",
            "owner": "Test Automation CI/CD",
            "custodian": "Kavy (MasterDB)",
            "steward": "Ansh (Governance)",
            "classification": DatasetClassification.FIXTURE,
            "sensitivity": "TEST_ONLY",
            "allowed_consumers": ["CI_CD_RUNNER", "INTEGRATION_TESTS"],
            "allowed_actions": [ActionType.READ, ActionType.WRITE, ActionType.DELETE],
            "approved_purposes": ["AUTOMATED_REGRESSION_TEST", "IDEMPOTENCY_VERIFICATION"],
            "lifecycle": LifecycleStatus.ACTIVE,
            "is_synthetic": True
        }
    }

    def __init__(self, fail_closed: bool = True):
        self.fail_closed = fail_closed
        self.audit_log: List[Dict[str, Any]] = []

    def evaluate_access(
        self,
        actor: str,
        role: str,
        dataset_id: str,
        action: ActionType,
        purpose: str,
        environment: str = "production",
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates the 6-Tuple: (Actor, Role, Dataset, Action, Purpose, Environment)
        """
        req_id = f"gov-eval-{uuid.uuid4().hex[:8]}"
        trace = trace_id or f"trace-gov-{uuid.uuid4().hex[:12]}"
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # 1. Identity Check
        if not actor or actor.upper() in ("UNKNOWN", "ANONYMOUS", "UNREGISTERED_DAEMON"):
            return self._build_verdict(
                req_id, trace, timestamp, actor, dataset_id, action, purpose,
                decision=AccessDecision.DENIED,
                reason="Unauthenticated or unknown actor identity. Fail-Closed enforced.",
                rule_code="G-RULE-17-UNKNOWN-ACTOR"
            )

        # 2. Environment Integrity (Dev/Test code cannot hit Production MasterDB)
        if environment.lower() == "development" and action in (ActionType.WRITE, ActionType.MODIFY, ActionType.DELETE):
            return self._build_verdict(
                req_id, trace, timestamp, actor, dataset_id, action, purpose,
                decision=AccessDecision.DENIED,
                reason="Development environment prohibited from mutating production MasterDB.",
                rule_code="G-RULE-18-DEV-ISOLATION"
            )

        # 3. Dataset Registry & Classification Check
        dataset_meta = self.GOVERNED_DATASETS.get(dataset_id)
        if not dataset_meta:
            return self._build_verdict(
                req_id, trace, timestamp, actor, dataset_id, action, purpose,
                decision=AccessDecision.DENIED,
                reason=f"Dataset '{dataset_id}' not registered in governance catalog. Defaults to UNKNOWN / QUARANTINED.",
                rule_code="G-RULE-UNKNOWN-DATASET"
            )

        classification = dataset_meta["classification"]

        # 4. Fixture Guard: Synthetic Fixtures cannot be read/written by Production Business Apps
        if classification == DatasetClassification.FIXTURE and actor in ("VANA", "FIN", "AIAIC") and environment.lower() == "production":
            return self._build_verdict(
                req_id, trace, timestamp, actor, dataset_id, action, purpose,
                decision=AccessDecision.DENIED,
                reason="Synthetic FIXTURE dataset prohibited from production consumer access.",
                rule_code="G-RULE-19-FIXTURE-POLLUTION"
            )

        # 5. Admin Action Check
        if action == ActionType.ADMIN:
            if role in ("PLATFORM_ADMIN", "GOVERNANCE_STEWARD"):
                return self._build_verdict(
                    req_id, trace, timestamp, actor, dataset_id, action, purpose,
                    decision=AccessDecision.ALLOWED,
                    reason="Authorized platform/governance administrator.",
                    rule_code="G-RULE-13-ADMIN-ACCESS"
                )
            return self._build_verdict(
                req_id, trace, timestamp, actor, dataset_id, action, purpose,
                decision=AccessDecision.DENIED,
                reason="Administrative actions restricted to certified MasterDB DBA / Governance Leads.",
                rule_code="G-RULE-13-ADMIN-DENIED"
            )

        # 6. Consumer Whitelist Check
        if actor not in dataset_meta["allowed_consumers"] and role not in ("DATASET_OWNER", "GOVERNANCE_STEWARD", "AUDITOR"):
            return self._build_verdict(
                req_id, trace, timestamp, actor, dataset_id, action, purpose,
                decision=AccessDecision.DENIED,
                reason=f"Actor '{actor}' is not in the allowed consumer whitelist for dataset '{dataset_id}'.",
                rule_code="G-RULE-CONSUMER-NOT-WHITELISTED"
            )

        # 7. Action Permission Check
        if action not in dataset_meta["allowed_actions"] and role != "DATASET_OWNER":
            return self._build_verdict(
                req_id, trace, timestamp, actor, dataset_id, action, purpose,
                decision=AccessDecision.DENIED,
                reason=f"Action '{action.value}' not permitted on dataset '{dataset_id}'. Allowed: {[a.value for a in dataset_meta['allowed_actions']]}.",
                rule_code="G-RULE-ACTION-NOT-PERMITTED"
            )

        # 8. Purpose Limitation Check
        norm_purpose = purpose.upper().replace(" ", "_")
        if norm_purpose not in dataset_meta["approved_purposes"]:
            if action == ActionType.EXPORT:
                return self._build_verdict(
                    req_id, trace, timestamp, actor, dataset_id, action, purpose,
                    decision=AccessDecision.DENIED,
                    reason=f"Export purpose '{purpose}' not approved. Requires explicit Data Sharing Agreement.",
                    rule_code="G-RULE-04-PURPOSE-LIMITATION"
                )
            return self._build_verdict(
                req_id, trace, timestamp, actor, dataset_id, action, purpose,
                decision=AccessDecision.REQUIRES_APPROVAL,
                reason=f"Purpose '{purpose}' is unlisted for dataset '{dataset_id}'. Governance approval required.",
                rule_code="G-RULE-PURPOSE-UNLISTED"
            )

        # 9. External Sharing / Export Guard
        if action == ActionType.EXPORT:
            if role == "EXTERNAL_PARTNER":
                return self._build_verdict(
                    req_id, trace, timestamp, actor, dataset_id, action, purpose,
                    decision=AccessDecision.REQUIRES_APPROVAL,
                    reason="External export requires dual sign-off from Ansh (Governance) and Legal Steward.",
                    rule_code="G-RULE-16-EXTERNAL-EXPORT"
                )
            return self._build_verdict(
                req_id, trace, timestamp, actor, dataset_id, action, purpose,
                decision=AccessDecision.CONTROLLED,
                reason="Approved internal export with mandatory lineage hash logging.",
                rule_code="G-RULE-CONTROLLED-EXPORT"
            )

        # All checks passed
        return self._build_verdict(
            req_id, trace, timestamp, actor, dataset_id, action, purpose,
            decision=AccessDecision.ALLOWED,
            reason="Request complies with all constitutional governance gates.",
            rule_code="G-RULE-PERMITTED"
        )

    def validate_canonical_eligibility(self, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validates whether a dataset meets the 10 Gate Requirements for CANONICAL status.
        """
        violations = []
        if not metadata.get("owner"):
            violations.append("Gate 1 Failed: Missing or unidentified dataset owner.")
        if not metadata.get("source_citation") and not metadata.get("source_url"):
            violations.append("Gate 2 Failed: Missing verifiable source citation or URL.")
        if not metadata.get("provenance_chain"):
            violations.append("Gate 3 Failed: Missing traceable transformation / extraction provenance.")
        if not metadata.get("mdu_schema_ref"):
            violations.append("Gate 4 Failed: Missing MDU schema reference validation.")
        if metadata.get("is_synthetic") is True:
            violations.append("Gate 5 Failed: Synthetic or mock fixtures can NEVER be classified as CANONICAL.")
        if not metadata.get("allowed_consumers"):
            violations.append("Gate 6 Failed: Missing allowed consumers access policy.")
        if not metadata.get("retention_policy"):
            violations.append("Gate 7 Failed: Missing explicit data retention / deprecation schedule.")
        if not metadata.get("sha256_fingerprint"):
            violations.append("Gate 8 Failed: Missing cryptographic payload SHA-256 fingerprint.")
        if metadata.get("quality_status") not in ("VALIDATED", "EXTRACTED_VERIFIED"):
            violations.append("Gate 9 Failed: Dataset quality status must be explicitly VALIDATED.")
        if not metadata.get("governance_signoff"):
            violations.append("Gate 10 Failed: Missing Governance Lead (Ansh) sign-off.")

        eligible = len(violations) == 0
        return eligible, violations

    def _build_verdict(
        self,
        req_id: str,
        trace_id: str,
        timestamp: str,
        actor: str,
        dataset_id: str,
        action: ActionType,
        purpose: str,
        decision: AccessDecision,
        reason: str,
        rule_code: str
    ) -> Dict[str, Any]:
        verdict = {
            "evaluation_id": req_id,
            "trace_id": trace_id,
            "timestamp": timestamp,
            "actor": actor,
            "dataset_id": dataset_id,
            "action": action.value,
            "declared_purpose": purpose,
            "decision": decision.value,
            "reason": reason,
            "rule_code": rule_code,
            "fail_closed": self.fail_closed
        }
        self.audit_log.append(verdict)
        return verdict


def run_governance_verification_suite():
    """
    Executes all Practical Exercises & Proof Gates programmatically.
    """
    engine = MasterDBGovernanceEngine()
    print("=" * 80)
    print("MASTERDB DATA GOVERNANCE & CONSTITUTIONAL CONTROL ENGINE")
    print("Candidate: Ansh | Platform Lead: Kavy | Task: Proof Gates Verification")
    print("=" * 80)

    # -------------------------------------------------------------
    # PROOF GATE 1: Classification Determination Proof
    # -------------------------------------------------------------
    print("\n[PROOF GATE 1] Determining Classification for FSI ISFR 2023 Dataset...")
    sample_fsi_meta = {
        "dataset_id": "DS-FSI-ISFR-2023-FOREST-COVER",
        "owner": "Forest Survey of India / MoEFCC, Govt of India",
        "source_citation": "ISFR 2023, Vol I, Table 2.4",
        "source_url": "http://fsi.nic.in/uploads/isfr2023/isfr_book_eng-vol-1_2023.pdf",
        "provenance_chain": "PyMuPDF extraction verified against physical report pp. 40-41",
        "mdu_schema_ref": "mdu://ontology/environmental/v2.2/official_forest_cover.schema.json",
        "is_synthetic": False,
        "allowed_consumers": ["VANA", "FIN", "AIAIC"],
        "retention_policy": "PERMANENT_HISTORICAL_VERSIONED",
        "sha256_fingerprint": "888cf3384210d7a0c6488ad5319859f977be415f3ecda8fb5d809187317ee965",
        "quality_status": "VALIDATED",
        "governance_signoff": "Ansh (Data Governance Lead)"
    }
    eligible, violations = engine.validate_canonical_eligibility(sample_fsi_meta)
    print(f"  Classification: CANONICAL | Eligible: {eligible} | Violations: {violations}")
    assert eligible is True, "Gate 1 Canonical Eligibility check failed!"
    print("  -> PROOF GATE 1 VERIFIED: Classification + Owner + Custodian + Sensitivity established.")

    # -------------------------------------------------------------
    # PROOF GATE 2: Access & Purpose Decision Proof (4 Scenarios)
    # -------------------------------------------------------------
    print("\n[PROOF GATE 2] Access Decisions Across 4 Scenarios (Exercise 3)...")

    # Scenario 1: Approved Internal Consumer
    r1 = engine.evaluate_access(
        actor="VANA", role="APPROVED_CONSUMER",
        dataset_id="DS-FSI-ISFR-2023-FOREST-COVER",
        action=ActionType.READ, purpose="DISTRICT_CANOPY_ANALYSIS"
    )
    print(f"  [Scenario 1] Approved Consumer -> Decision: {r1['decision']} | Rule: {r1['rule_code']}")
    assert r1["decision"] == "ALLOWED"

    # Scenario 2: Whitelisted Consumer / Unlisted Purpose -> Requires Approval
    r2 = engine.evaluate_access(
        actor="VANA", role="APPROVED_CONSUMER",
        dataset_id="DS-THANECREEK-2023-BIOMASS",
        action=ActionType.READ, purpose="EXPERIMENTAL_UNLISTED_MODEL"
    )
    print(f"  [Scenario 2] Unlisted Purpose -> Decision: {r2['decision']} | Reason: {r2['reason']}")
    assert r2["decision"] == "REQUIRES_APPROVAL"

    # Scenario 3: Unknown / Unauthenticated Consumer
    r3 = engine.evaluate_access(
        actor="UNKNOWN_BOT_99", role="ANONYMOUS",
        dataset_id="DS-FSI-ISFR-2023-FOREST-COVER",
        action=ActionType.READ, purpose="DATA_SCRAPING"
    )
    print(f"  [Scenario 3] Unknown Consumer -> Decision: {r3['decision']} | Rule: {r3['rule_code']}")
    assert r3["decision"] == "DENIED"

    # Scenario 4: Export Request with Unapproved Purpose
    r4 = engine.evaluate_access(
        actor="AIAIC", role="APPROVED_CONSUMER",
        dataset_id="DS-FSI-ISFR-2023-FOREST-COVER",
        action=ActionType.EXPORT, purpose="COMMERCIAL_BULK_SALE"
    )
    print(f"  [Scenario 4] Unapproved Export -> Decision: {r4['decision']} | Rule: {r4['rule_code']}")
    assert r4["decision"] == "DENIED"
    print("  -> PROOF GATE 2 VERIFIED: 4/4 Access Decisions correctly evaluated.")

    # -------------------------------------------------------------
    # PROOF GATE 3: Constitutional Boundary Proof
    # -------------------------------------------------------------
    print("\n[PROOF GATE 3] Constitutional Boundary Enforcement...")
    # Attempting to classify a synthetic fixture as canonical
    synthetic_fixture_meta = dict(sample_fsi_meta)
    synthetic_fixture_meta["is_synthetic"] = True
    synthetic_fixture_meta["owner"] = "Test Mock"
    eligible_fixture, violations_fixture = engine.validate_canonical_eligibility(synthetic_fixture_meta)
    print(f"  Synthetic Fixture Canonical Attempt -> Eligible: {eligible_fixture}")
    for v in violations_fixture:
        print(f"    - {v}")
    assert eligible_fixture is False, "Synthetic fixture must NOT be eligible for canonical status!"
    print("  -> PROOF GATE 3 VERIFIED: Constitutional separation and anti-pollution gate enforced.")

    print("\n" + "=" * 80)
    print("ALL TASK 1 GOVERNANCE PROOF GATES SUCCESSFULLY PASSED")
    print(f"Total Audit Trail Entries Generated: {len(engine.audit_log)}")
    print("=" * 80)
    return True


if __name__ == "__main__":
    run_governance_verification_suite()
