"""
VANA / FIN Review Orchestrator — Lifecycle & Compliance Orchestration
====================================================================
Task ID: T-GOV-F01 (Remediation & Structural Compliance)
Candidate / Assignee: Ansh Gupta (Spatial / GIS & Governance Lead)
Product Governance: BHIV / Parikshak / Niyantran

Orchestrates candidate task evaluation, Review Packet structural verification,
state machine transitions, and automated compliance auditing.
"""

from enum import Enum
import hashlib
import json
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from evaluation_engine.rule_engine import VanaRuleEngine, VanaEvaluationRequest, VanaEvaluationResponse

logger = logging.getLogger("vana_review_orchestrator")


class ReviewStage(str, Enum):
    INITIAL_INGEST = "INITIAL_INGEST"
    STATIC_ANALYSIS = "STATIC_ANALYSIS"
    RULE_EVALUATION = "RULE_EVALUATION"
    CONSTITUTIONAL_AUDIT = "CONSTITUTIONAL_AUDIT"
    VERIFIED_COMPLETE = "VERIFIED_COMPLETE"
    FAILED = "FAILED"


class DecisionState(str, Enum):
    PENDING = "PENDING"
    PASS = "PASS"
    FAIL = "FAIL"
    REMEDIATION_REQUIRED = "REMEDIATION_REQUIRED"


class ReviewPacketContract(BaseModel):
    entry_point: str = Field(..., min_length=10)
    core_flow: str = Field(..., min_length=30)
    live_flow: str = Field(..., min_length=20)
    output_sample: Dict[str, Any] = Field(...)
    self_audit_score: float = Field(..., ge=0.0, le=100.0)

    def validate_keys(self) -> bool:
        required_keys = {"evaluation_result", "failure_type", "trace_id"}
        return required_keys.issubset(self.output_sample.keys())


class CandidateReviewRecord(BaseModel):
    task_id: str
    candidate_name: str
    stage: ReviewStage
    decision: DecisionState
    score: float
    pac: Dict[str, int]
    rubric: Dict[str, int]
    failure_type: Optional[str] = None
    audit_trail: List[str] = Field(default_factory=list)
    state_hash: str
    created_at: str


class VanaReviewOrchestrator:
    """
    Lifecycle orchestrator that processes candidate submissions through strict
    Parikshak gates and ensures architectural & structural compliance.
    """

    def __init__(self, rule_engine: Optional[VanaRuleEngine] = None):
        self.rule_engine = rule_engine or VanaRuleEngine()

    def parse_review_packet_markdown(self, markdown_content: str) -> Dict[str, Any]:
        """
        Parse REVIEW_PACKET.md content adhering to Parikshak's Phase 1 Hard Gate parser rules:
        - Structure-aware header detection (## heading only)
        - Required sections in exact order: ENTRY POINT, CORE FLOW, LIVE FLOW, OUTPUT SAMPLE
        - Strict JSON extraction from fenced code block
        """
        required_sections = ["ENTRY POINT", "CORE FLOW", "LIVE FLOW", "OUTPUT SAMPLE"]

        # Extract ## headers
        header_pattern = re.compile(r"^##\s+([A-Za-z0-9_ -]+)$", re.MULTILINE)
        headers_found = [m.group(1).strip().upper() for m in header_pattern.finditer(markdown_content)]

        missing = [sec for sec in required_sections if sec not in headers_found]
        if missing:
            return {
                "valid": False,
                "error": f"Missing required sections: {', '.join(missing)}",
                "missing_sections": missing
            }

        # Check ordering
        indices = [headers_found.index(sec) for sec in required_sections]
        if indices != sorted(indices):
            return {
                "valid": False,
                "error": f"Sections out of order: expected {required_sections}, got {headers_found}"
            }

        # Extract sections content
        sections: Dict[str, str] = {}
        for i, sec in enumerate(required_sections):
            curr_header = f"## {sec}"
            start_pos = markdown_content.find(curr_header)
            if start_pos == -1:
                # case-insensitive search
                match = re.search(rf"^##\s+{re.escape(sec)}\b", markdown_content, re.IGNORECASE | re.MULTILINE)
                start_pos = match.start() if match else -1

            if start_pos != -1:
                content_start = start_pos + len(curr_header)
                if i < len(required_sections) - 1:
                    next_sec = required_sections[i + 1]
                    next_match = re.search(rf"^##\s+{re.escape(next_sec)}\b", markdown_content[content_start:], re.IGNORECASE | re.MULTILINE)
                    end_pos = content_start + next_match.start() if next_match else len(markdown_content)
                else:
                    # After OUTPUT SAMPLE, stop at next ## header if any
                    next_match = re.search(r"^##\s+[A-Za-z0-9_ -]+$", markdown_content[content_start:], re.MULTILINE)
                    end_pos = content_start + next_match.start() if next_match else len(markdown_content)

                sections[sec] = markdown_content[content_start:end_pos].strip()

        # Validate JSON block in OUTPUT SAMPLE
        output_sample_text = sections.get("OUTPUT SAMPLE", "")
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", output_sample_text, re.DOTALL)
        if not json_match:
            return {
                "valid": False,
                "error": "OUTPUT SAMPLE section is missing fenced JSON code block"
            }

        try:
            sample_json = json.loads(json_match.group(1))
        except Exception as e:
            return {
                "valid": False,
                "error": f"OUTPUT SAMPLE JSON is malformed: {e}"
            }

        # Verify required keys in output_sample
        required_keys = {"evaluation_result", "failure_type", "trace_id"}
        if not required_keys.issubset(sample_json.keys()):
            return {
                "valid": False,
                "error": f"OUTPUT SAMPLE JSON missing required keys: {required_keys - set(sample_json.keys())}"
            }

        return {
            "valid": True,
            "sections": sections,
            "output_sample_data": sample_json
        }

    def orchestrate_submission(
        self,
        task_id: str,
        candidate_name: str,
        review_packet_text: str,
        evaluation_request: Optional[VanaEvaluationRequest] = None
    ) -> CandidateReviewRecord:
        """
        Execute full lifecycle orchestration:
        1. Ingest submission
        2. Validate Review Packet syntax & ordering
        3. Execute deterministic Rule Engine checks
        4. Generate immutable state hash and audit log
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        audit_trail: List[str] = [f"[{now_iso}] Ingested task '{task_id}' for candidate '{candidate_name}'."]

        # Step 1: Parse and validate review packet
        packet_result = self.parse_review_packet_markdown(review_packet_text)
        if not packet_result["valid"]:
            audit_trail.append(f"Review Packet failed validation: {packet_result['error']}")
            state_hash = hashlib.sha256(f"{task_id}:FAIL:schema_violation".encode()).hexdigest()
            return CandidateReviewRecord(
                task_id=task_id,
                candidate_name=candidate_name,
                stage=ReviewStage.FAILED,
                decision=DecisionState.FAIL,
                score=16.0,
                pac={"code": 0, "architecture": 0, "proof": 0},
                rubric={"has_alignment": 0, "has_effort": 0, "has_code": 0},
                failure_type="schema_violation",
                audit_trail=audit_trail,
                state_hash=state_hash,
                created_at=now_iso
            )

        audit_trail.append("Review Packet parsed successfully: all required sections and JSON blocks valid.")

        # Step 2: Evaluate rules
        req = evaluation_request or VanaEvaluationRequest(
            actor="VANA",
            role="APPROVED_CONSUMER",
            dataset_id="DS-FSI-ISFR-2023-FOREST-COVER",
            action="READ",
            purpose="DISTRICT_CANOPY_ANALYSIS",
            environment="production",
            carbon_payload={"measured_agb": 84.83, "estimated_agb": 111.31, "silently_mixed": False},
            is_synthetic=False
        )

        eval_resp = self.rule_engine.evaluate(req)
        audit_trail.append(f"Rule Engine evaluation completed: Result={eval_resp.evaluation_result}, Score={eval_resp.score}.")

        if eval_resp.evaluation_result == "PASS":
            stage = ReviewStage.VERIFIED_COMPLETE
            decision = DecisionState.PASS
            audit_trail.append("Task verification successful: All strict quality gates and proof gates verified.")
        else:
            stage = ReviewStage.FAILED
            decision = DecisionState.REMEDIATION_REQUIRED
            audit_trail.append(f"Task verification failed with failure_type='{eval_resp.failure_type}'.")

        return CandidateReviewRecord(
            task_id=task_id,
            candidate_name=candidate_name,
            stage=stage,
            decision=decision,
            score=eval_resp.score,
            pac=eval_resp.pac,
            rubric=eval_resp.rubric,
            failure_type=eval_resp.failure_type,
            audit_trail=audit_trail,
            state_hash=eval_resp.state_hash,
            created_at=now_iso
        )
