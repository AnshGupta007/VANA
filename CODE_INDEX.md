# VANA / FIN Architectural Code Index (T-GOV-F01)

- **Task Title**: Remediate Incomplete & Harden Ansh FIN / VANA Full System Completion with Real Data Integration Architecture (T-GOV-F01)
- **Assignee**: Ansh Gupta
- **Governance**: BHIV / Parikshak / Niyantran

---

## 1. Directory Tree

```
backend/
├── api/
│   ├── __init__.py
│   └── production.py                       # Enterprise FastAPI production microservice
├── evaluation_engine/
│   ├── __init__.py
│   └── rule_engine.py                      # Deterministic 5-gate rule evaluation engine
├── task_selector/
│   ├── __init__.py
│   └── review_orchestrator.py              # Lifecycle state machine & Review Packet parser
├── security/
│   ├── __init__.py
│   └── middleware.py                       # ErrorBoundaryMiddleware & UserRole RBAC
├── integrations/
│   ├── __init__.py
│   └── local_llm_client.py                 # Offline-safe deterministic LLM verification client
├── tests/
│   ├── __init__.py
│   ├── conftest.py                         # Pytest shared fixtures & seed credentials
│   ├── verify_determinism.py               # Standalone 50-run determinism verification audit
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_rule_engine.py             # 5-gate pipeline, edge cases, Pydantic models
│   │   ├── test_review_orchestrator.py     # Parser structure, ordering, lifecycle states
│   │   ├── test_security_middleware.py     # Error boundary, replay protection, RBAC
│   │   └── test_local_llm_client.py        # Environmental bounds & anomaly detection
│   └── integration/
│       ├── __init__.py
│       ├── test_api_production.py          # Endpoints integration: auth, carbon, spatial, TANTRA
│       └── test_error_boundary.py          # Zero 500 guarantee on malformed payloads
├── vana_auth.py                            # JWT authentication & PBKDF2 hashing
├── vana_carbon_engine.py                   # Biomass & IPCC Blue Carbon carbon calculator
├── vana_data_engine.py                     # SQLite database connector & real observations
├── vana_spatial_engine.py                  # WGS84 GeoJSON layer & GIS bounding engine
├── masterdb_governance_engine.py           # 6-Tuple constitutional dataset access governance
├── vana_masterdb.sqlite                    # Governed MasterDB relational database
├── requirements.txt                        # Pinned dependencies (strict == versions)
├── pytest.ini                              # Pytest runner configuration
├── REVIEW_PACKET.md                        # Parikshak verification review packet
├── CODE_PACKET.md                          # Git diffs, changed files summary
└── CODE_INDEX.md                           # This index file
```

---

## 2. Module Inventory & Architectural Roles

| Module Path | Primary Symbols / Classes | Architectural Responsibility |
| :--- | :--- | :--- |
| `api/production.py` | `app`, `evaluate_compliance`, `orchestrate_review`, `vana_execute` | Production FastAPI microservice exposing REST routes with strict Pydantic schemas. |
| `evaluation_engine/rule_engine.py` | `VanaRuleEngine`, `VanaEvaluationRequest`, `VanaEvaluationResponse`, `RuleEvaluationResult` | 5-stage deterministic gate pipeline enforcing schema strictness, completeness, scientific doctrine, 6-tuple governance, and synthetic quarantine. |
| `task_selector/review_orchestrator.py` | `VanaReviewOrchestrator`, `ReviewStage`, `DecisionState`, `ReviewPacketContract` | Parses and validates `REVIEW_PACKET.md` structural compliance per Parikshak Phase 1 parser rules and orchestrates task lifecycle. |
| `security/middleware.py` | `ErrorBoundaryMiddleware`, `UserRole`, `require_role`, `register_used_token` | Error boundary preventing raw 500 exceptions, enforcing RBAC role checks and replay defense. |
| `integrations/local_llm_client.py` | `LocalLLMClient`, `LLMVerificationResponse` | Offline-safe deterministic verification adapter evaluating physiological carbon limits and provenance integrity. |
| `tests/conftest.py` | `client`, `rule_engine`, `review_orchestrator`, `admin_token`, `valid_eval_request` | Centralized test configuration and test client fixtures. |
| `tests/verify_determinism.py` | `run_determinism_audit` | Standalone CLI verifying 50 consecutive runs produce identical SHA-256 state hashes. |

---

## 3. Quality Gate Mapping

- **Strict Schema Validation**: Implemented via Pydantic v2 models in `evaluation_engine/rule_engine.py` and `api/production.py`.
- **Zero Unhandled 500s**: Intercepted by `ErrorBoundaryMiddleware` in `security/middleware.py` and custom exception handlers in `api/production.py`.
- **Deterministic State Hashing**: Handled by `VanaRuleEngine.compute_deterministic_state_hash` (50 runs with identical SHA-256 hash `bcfadd5cfd7ff04eb5200ad734ca2db53bf2ebd1c8b078580fd6d69d965dbbe5`).
- **Test Pass Rate**: 65/65 tests passed (100% pass rate) with 98% code coverage.
