"""
Pytest Fixtures for VANA / FIN Architectural Hardening & Verification
====================================================================
Task ID: T-GOV-F01
Assignee: Ansh Gupta
"""

import pytest
from fastapi.testclient import TestClient

from api.production import app
from vana_auth import create_access_token, SEED_ACCOUNTS
from evaluation_engine.rule_engine import VanaRuleEngine, VanaEvaluationRequest
from task_selector.review_orchestrator import VanaReviewOrchestrator
from integrations.local_llm_client import LocalLLMClient


@pytest.fixture(scope="session")
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def rule_engine():
    """VanaRuleEngine instance fixture."""
    return VanaRuleEngine()


@pytest.fixture(scope="session")
def review_orchestrator():
    """VanaReviewOrchestrator instance fixture."""
    return VanaReviewOrchestrator()


@pytest.fixture(scope="session")
def local_llm():
    """LocalLLMClient instance fixture."""
    return LocalLLMClient()


@pytest.fixture(scope="session")
def admin_token():
    """Generate valid JWT token for admin role."""
    admin_acc = next(a for a in SEED_ACCOUNTS if a["role"] == "admin")
    return create_access_token(admin_acc)


@pytest.fixture(scope="session")
def participant_token():
    """Generate valid JWT token for participant role."""
    part_acc = next(a for a in SEED_ACCOUNTS if a["role"] == "participant")
    return create_access_token(part_acc)


@pytest.fixture(scope="session")
def judge_token():
    """Generate valid JWT token for judge role."""
    judge_acc = next(a for a in SEED_ACCOUNTS if a["role"] == "judge")
    return create_access_token(judge_acc)


@pytest.fixture(scope="session")
def steward_token():
    """Generate valid JWT token for steward role."""
    steward_acc = next(a for a in SEED_ACCOUNTS if a["role"] == "steward")
    return create_access_token(steward_acc)


@pytest.fixture
def valid_eval_request():
    """Valid standard evaluation request payload."""
    return VanaEvaluationRequest(
        actor="VANA",
        role="APPROVED_CONSUMER",
        dataset_id="DS-FSI-ISFR-2023-FOREST-COVER",
        action="READ",
        purpose="DISTRICT_CANOPY_ANALYSIS",
        environment="production",
        carbon_payload={"measured_agb": 84.83, "estimated_agb": 111.31, "silently_mixed": False},
        is_synthetic=False
    )


@pytest.fixture
def valid_review_packet_markdown():
    """
    Standard markdown text conforming strictly to Parikshak Phase 1 Hard Gate parser rules:
    - Headers in exact order: ENTRY POINT, CORE FLOW, LIVE FLOW, OUTPUT SAMPLE
    - Fenced JSON code block in OUTPUT SAMPLE containing evaluation_result, failure_type, trace_id
    """
    return """# Parikshak Task Verification Review Packet
Task ID: T-GOV-F01
Assignee: Ansh Gupta

## ENTRY POINT
The primary production entry point for VANA is located in file api/production.py.
This FastAPI application mounts the production routes, security middleware, and evaluation engine.
All HTTP endpoints are exposed through this file.

## CORE FLOW
The architectural pipeline processes incoming environmental datasets through a multi-step deterministic engine.
The flow proceeds: Step 1 Schema Validation -> Step 2 Completeness Verification -> Step 3 Scientific Doctrine Separation -> Step 4 Constitutional 6-Tuple Access -> Step 5 Anti-Pollution Quarantine.
Each gate returns a scored rule result and updates the state machine.

## LIVE FLOW
Inbound requests are submitted via HTTP POST to the /api/v1/evaluate endpoint with JSON payloads.
The server responds with a deterministic evaluation response containing a SHA-256 state hash.
Clients can submit live requests to test endpoints and receive verified output.

## OUTPUT SAMPLE
Below is the verified deterministic execution output sample:
```json
{
  "evaluation_result": "PASS",
  "failure_type": null,
  "trace_id": "trace-parikshak-proof-tgovf01",
  "score": 100.0,
  "state_hash": "a1b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef0"
}
```

## ARCHITECTURAL PROOF
Verification completed with 100% test pass rate and zero unhandled 500 exceptions.
"""
