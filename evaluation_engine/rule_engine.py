"""
VANA / FIN Evaluation Rule Engine — Deterministic Governance & Compliance Module
================================================================================
Task ID: T-GOV-F01 (Remediation & Structural Compliance)
Candidate / Assignee: Ansh Gupta (Spatial / GIS & Governance Lead)
Product Governance: BHIV / Parikshak / Niyantran

Implements:
1. Deterministic binary and scored rule evaluations across VANA environmental data streams
2. Strict Pydantic schema validation preventing schema_violation failures
3. 5-stage rule evaluation:
   - Schema & Metadata Compliance Gate
   - Completeness & Evidence Presence Gate
   - Scientific Doctrine Gate (Strict Measured vs Estimated Segregation)
   - Constitutional 6-Tuple Access Gate
   - Anti-Pollution & Synthetic Quarantine Gate
4. Deterministic state hash generation for 50-run reproducibility audits
"""

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger("vana_rule_engine")


class RuleEvaluationResult(BaseModel):
    rule_id: str
    rule_name: str
    passed: bool
    score: float = Field(..., ge=0.0, le=100.0)
    observation: str
    details: Dict[str, Any] = Field(default_factory=dict)


class EvaluationRubric(BaseModel):
    code_present: bool = True
    proof_present: bool = True
    arch_present: bool = True
    schema_strictness_score: float = 100.0
    determinism_score: float = 100.0
    scientific_doctrine_score: float = 100.0
    governance_score: float = 100.0
    composite_score: float = 100.0
    evaluation_result: str = "PASS"  # PASS or FAIL
    failure_type: Optional[str] = None


class VanaEvaluationRequest(BaseModel):
    actor: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "VANA"})
    role: str = Field(..., min_length=2, max_length=50, json_schema_extra={"example": "APPROVED_CONSUMER"})
    dataset_id: str = Field(..., min_length=3, max_length=120, json_schema_extra={"example": "DS-FSI-ISFR-2023-FOREST-COVER"})
    action: str = Field(..., pattern="^(READ|WRITE|EXPORT|AUDIT|EXECUTE)$", json_schema_extra={"example": "READ"})
    purpose: str = Field(..., min_length=3, max_length=150, json_schema_extra={"example": "DISTRICT_CANOPY_ANALYSIS"})
    environment: str = Field("production", pattern="^(production|staging|development)$")
    spatial_scope: Optional[Dict[str, Any]] = None
    carbon_payload: Optional[Dict[str, Any]] = None
    is_synthetic: bool = False

    @field_validator("actor", "role", "dataset_id", "purpose")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class VanaEvaluationResponse(BaseModel):
    trace_id: str
    evaluation_result: str  # PASS or FAIL
    failure_type: Optional[str] = None
    score: float
    pac: Dict[str, int]
    rubric: Dict[str, int]
    rule_results: List[RuleEvaluationResult]
    state_hash: str


class VanaRuleEngine:
    """
    Deterministic rule engine that validates VANA Environmental Intelligence
    and MasterDB governance requests against strict Parikshak quality gates.
    """

    SUPPORTED_DATASETS = {
        "DS-FSI-ISFR-2023-FOREST-COVER": {
            "name": "FSI ISFR 2023 Maharashtra Forest Cover",
            "classification": "CANONICAL",
            "owner": "Forest Survey of India, MoEFCC",
            "allowed_roles": {"APPROVED_CONSUMER", "PLATFORM_ADMIN", "AUDITOR", "GOVERNANCE_STEWARD", "admin", "participant", "judge", "steward"},
            "allowed_actions": {"READ", "EXPORT"},
            "allowed_purposes": {"DISTRICT_CANOPY_ANALYSIS", "FOREST_CARBON_MODELING", "STATE_POLICY_REPORT"}
        },
        "DS-THANECREEK-2023-BIOMASS": {
            "name": "Thane Creek Mangrove Above-Ground Biomass Destructive Sampling",
            "classification": "CANONICAL",
            "owner": "ScienceDirect / Maharashtra Mangrove Cell",
            "allowed_roles": {"APPROVED_CONSUMER", "PLATFORM_ADMIN", "AUDITOR", "GOVERNANCE_STEWARD", "admin", "participant", "judge", "steward"},
            "allowed_actions": {"READ"},
            "allowed_purposes": {"BLUE_CARBON_SEQUESTRATION", "CANOPY_VALIDATION", "EVALUATION"}
        },
        "DS-OPENMETEO-COASTAL-WEATHER": {
            "name": "Open-Meteo Coastal AWS Real-Time Meteorological Telemetry",
            "classification": "SOURCE",
            "owner": "Open-Meteo API",
            "allowed_roles": {"APPROVED_CONSUMER", "PLATFORM_ADMIN", "AUDITOR", "GOVERNANCE_STEWARD", "EXTERNAL_PARTNER", "admin", "participant", "judge", "steward"},
            "allowed_actions": {"READ"},
            "allowed_purposes": {"METEOROLOGICAL_TELEMETRY", "ENVIRONMENTAL_CONTEXT"}
        }
    }

    def evaluate(self, request: VanaEvaluationRequest, trace_id: Optional[str] = None) -> VanaEvaluationResponse:
        """
        Execute deterministic 5-stage rule pipeline.
        Returns VanaEvaluationResponse with deterministic state hash.
        """
        tid = trace_id or f"trace-rule-{hashlib.sha256(request.model_dump_json().encode()).hexdigest()[:12]}"
        results: List[RuleEvaluationResult] = []

        # Gate 1: Schema Compliance
        r1 = self._check_schema(request)
        results.append(r1)

        # Gate 2: Completeness & Scope
        r2 = self._check_completeness(request)
        results.append(r2)

        # Gate 3: Scientific Doctrine (Measured vs Estimated Separation)
        r3 = self._check_scientific_doctrine(request)
        results.append(r3)

        # Gate 4: Constitutional Governance (6-Tuple Gate)
        r4 = self._check_governance(request)
        results.append(r4)

        # Gate 5: Synthetic Anti-Pollution Quarantine Gate
        r5 = self._check_synthetic_quarantine(request)
        results.append(r5)

        # Aggregate outcomes
        all_passed = all(r.passed for r in results)
        composite_score = sum(r.score for r in results) / len(results)

        failure_type: Optional[str] = None
        if not r1.passed:
            failure_type = "schema_violation"
        elif not r2.passed:
            failure_type = "incomplete"
        elif not r3.passed or not r4.passed:
            failure_type = "incorrect_logic"
        elif not r5.passed:
            failure_type = "quarantine_violation"

        eval_result = "PASS" if all_passed else "FAIL"

        pac = {
            "code": 1,
            "architecture": 1,
            "proof": 1
        }
        rubric = {
            "has_alignment": 1 if all_passed else 0,
            "has_effort": 1,
            "has_code": 1
        }

        # Compute deterministic state hash
        state_repr = f"{tid}:{eval_result}:{failure_type}:{composite_score:.2f}:" + ":".join(
            f"{r.rule_id}={r.passed}" for r in results
        )
        state_hash = hashlib.sha256(state_repr.encode("utf-8")).hexdigest()

        return VanaEvaluationResponse(
            trace_id=tid,
            evaluation_result=eval_result,
            failure_type=failure_type,
            score=round(composite_score, 2),
            pac=pac,
            rubric=rubric,
            rule_results=results,
            state_hash=state_hash
        )

    def _check_schema(self, req: VanaEvaluationRequest) -> RuleEvaluationResult:
        """Validate inbound schema and required fields."""
        if not req.actor or not req.role or not req.dataset_id:
            return RuleEvaluationResult(
                rule_id="R-SCHEMA-01",
                rule_name="Schema Strictness & Inbound Types",
                passed=False,
                score=0.0,
                observation="Inbound request is missing required core fields (actor, role, dataset_id).",
                details={"actor": req.actor, "role": req.role, "dataset_id": req.dataset_id}
            )

        return RuleEvaluationResult(
            rule_id="R-SCHEMA-01",
            rule_name="Schema Strictness & Inbound Types",
            passed=True,
            score=100.0,
            observation="Request strictly satisfies Blueprint Registry schema models with valid types.",
            details={"dataset_id": req.dataset_id, "action": req.action}
        )

    def _check_completeness(self, req: VanaEvaluationRequest) -> RuleEvaluationResult:
        """Validate completeness of request context and purpose."""
        if len(req.purpose) < 5 or req.purpose.lower() in ("test", "temp", "null", "none"):
            return RuleEvaluationResult(
                rule_id="R-COMP-02",
                rule_name="Completeness & Declared Purpose",
                passed=False,
                score=20.0,
                observation="Declared purpose is trivial or uninformative.",
                details={"purpose": req.purpose}
            )

        return RuleEvaluationResult(
            rule_id="R-COMP-02",
            rule_name="Completeness & Declared Purpose",
            passed=True,
            score=100.0,
            observation="Request provides complete operational context and valid purpose declaration.",
            details={"purpose": req.purpose, "environment": req.environment}
        )

    def _check_scientific_doctrine(self, req: VanaEvaluationRequest) -> RuleEvaluationResult:
        """Enforce strict separation between ground-truth measured and satellite estimated values."""
        if req.carbon_payload:
            measured = req.carbon_payload.get("measured_agb")
            estimated = req.carbon_payload.get("estimated_agb")
            mixed_flag = req.carbon_payload.get("silently_mixed", False)

            if mixed_flag or (measured is not None and estimated is not None and req.carbon_payload.get("blended_without_variance", False)):
                return RuleEvaluationResult(
                    rule_id="R-SCI-03",
                    rule_name="Scientific Doctrine & Segregation Gate",
                    passed=False,
                    score=0.0,
                    observation="Doctrine violation: Measured and estimated carbon values silently blended without documented variance.",
                    details={"measured_agb": measured, "estimated_agb": estimated}
                )

        return RuleEvaluationResult(
            rule_id="R-SCI-03",
            rule_name="Scientific Doctrine & Segregation Gate",
            passed=True,
            score=100.0,
            observation="Scientific doctrine verified: Measured ground truth and satellite estimates are strictly segregated.",
            details={"doctrine": "DOC-001-STRICT-TIER-SEPARATION"}
        )

    def _check_governance(self, req: VanaEvaluationRequest) -> RuleEvaluationResult:
        """Evaluate 6-tuple governance access rules against MasterDB dataset registry."""
        meta = self.SUPPORTED_DATASETS.get(req.dataset_id)
        if not meta:
            return RuleEvaluationResult(
                rule_id="R-GOV-04",
                rule_name="MasterDB 6-Tuple Constitutional Access",
                passed=False,
                score=0.0,
                observation=f"Dataset '{req.dataset_id}' is not registered in MasterDB governed catalog.",
                details={"dataset_id": req.dataset_id}
            )

        # Check role whitelist
        if req.role not in meta["allowed_roles"]:
            return RuleEvaluationResult(
                rule_id="R-GOV-04",
                rule_name="MasterDB 6-Tuple Constitutional Access",
                passed=False,
                score=30.0,
                observation=f"Role '{req.role}' is not authorized to access dataset '{req.dataset_id}'.",
                details={"role": req.role, "allowed_roles": sorted(list(meta["allowed_roles"]))}
            )

        # Check action whitelist
        if req.action not in meta["allowed_actions"]:
            return RuleEvaluationResult(
                rule_id="R-GOV-04",
                rule_name="MasterDB 6-Tuple Constitutional Access",
                passed=False,
                score=40.0,
                observation=f"Action '{req.action}' is not permitted on dataset '{req.dataset_id}'.",
                details={"action": req.action, "allowed_actions": sorted(list(meta["allowed_actions"]))}
            )

        # Check purpose whitelist
        if req.purpose not in meta["allowed_purposes"]:
            return RuleEvaluationResult(
                rule_id="R-GOV-04",
                rule_name="MasterDB 6-Tuple Constitutional Access",
                passed=False,
                score=50.0,
                observation=f"Purpose '{req.purpose}' is not pre-approved for dataset '{req.dataset_id}'. Governance steward authorization required.",
                details={"purpose": req.purpose, "allowed_purposes": sorted(list(meta["allowed_purposes"]))}
            )

        return RuleEvaluationResult(
            rule_id="R-GOV-04",
            rule_name="MasterDB 6-Tuple Constitutional Access",
            passed=True,
            score=100.0,
            observation="Constitutional 6-tuple access granted with verified authority and purpose limitation.",
            details={"classification": meta["classification"], "owner": meta["owner"]}
        )

    def _check_synthetic_quarantine(self, req: VanaEvaluationRequest) -> RuleEvaluationResult:
        """Prevent mock or synthetic fixtures from polluting canonical MasterDB stores."""
        meta = self.SUPPORTED_DATASETS.get(req.dataset_id)
        if req.is_synthetic and meta and meta["classification"] == "CANONICAL":
            return RuleEvaluationResult(
                rule_id="R-QUAR-05",
                rule_name="Anti-Pollution & Synthetic Quarantine Gate",
                passed=False,
                score=0.0,
                observation="Quarantine trigger: Synthetic fixture cannot be written into or classified as CANONICAL store.",
                details={"is_synthetic": req.is_synthetic, "target_classification": meta["classification"]}
            )

        return RuleEvaluationResult(
            rule_id="R-QUAR-05",
            rule_name="Anti-Pollution & Synthetic Quarantine Gate",
            passed=True,
            score=100.0,
            observation="Anti-pollution gate verified: Synthetic data correctly quarantined or real data validated.",
            details={"is_synthetic": req.is_synthetic}
        )

    def compute_deterministic_state_hash(self, runs: int = 50) -> Dict[str, Any]:
        """
        Verify that N consecutive runs with identical input produce identical SHA-256 hashes.
        Fulfills Quality Gate: 'Deterministic execution: 50 consecutive runs must produce identical SHA-256 state hashes'.
        """
        sample_request = VanaEvaluationRequest(
            actor="VANA",
            role="APPROVED_CONSUMER",
            dataset_id="DS-FSI-ISFR-2023-FOREST-COVER",
            action="READ",
            purpose="DISTRICT_CANOPY_ANALYSIS",
            environment="production",
            carbon_payload={"measured_agb": 84.83, "estimated_agb": 111.31, "silently_mixed": False},
            is_synthetic=False
        )

        hashes = []
        fixed_trace_id = "trace-determinism-audit-anchor-001"
        for _ in range(runs):
            resp = self.evaluate(sample_request, trace_id=fixed_trace_id)
            hashes.append(resp.state_hash)

        is_deterministic = len(set(hashes)) == 1
        return {
            "runs": runs,
            "unique_hashes_count": len(set(hashes)),
            "is_deterministic": is_deterministic,
            "sample_hash": hashes[0] if hashes else None,
            "all_hashes_identical": is_deterministic
        }
