# MASTERDB CONSTITUTIONAL ACCESS CONTROL MATRIX

**Document Identifier:** MASTERDB-ACM-V1.0  
**Candidate / Author:** Ansh (Data Governance & Constitutional Controls)  
**Collaborator:** Kavy (MASTERDB Platform Lead)  
**Dependencies:** TANTRA (Runtime Enforcement), MDU (Semantics), Bucket (Evidence)  
**Scope:** BHIV Governed Data Platform / VANA Ecosystem  
**Date:** September 2026  

---

## 1. Governance Access Model Specification

Access to MASTERDB is **never** granted solely on the basis of a network IP or an API key. In accordance with **Task 1E**, every access request is evaluated against the 6-tuple governance contract:

$$\text{Decision} = \text{Evaluate}(\text{Actor Identity}, \text{Role}, \text{Dataset Classification}, \text{Declared Purpose}, \text{Environment}, \text{Action})$$

### 1.1 Action Definitions
* **READ**: Query and retrieve structured observation, measurement, and spatial records.
* **WRITE**: Ingest new source, observation, or measurement payloads through the canonical validation pipeline.
* **MODIFY**: Append versioned modifications or corrections (destructive in-place updates are blocked on canonical data).
* **DELETE**: Soft-delete, archive, or purge records according to approved retention schedules.
* **EXPORT**: Extract datasets outside the BHIV boundary to third parties or local filesystem bundles.
* **ADMIN**: Alter database schemas, execute migrations, manage indexes, and modify access credentials.

### 1.2 Decision Outcomes
* **`ALLOWED`**: Request complies with all constitutional gates; executed immediately with audit trace.
* **`CONTROLLED`**: Permitted with rate-limiting, field-level masking, or explicit row-level filters applied.
* **`REQUIRES_APPROVAL`**: Blocked pending out-of-band cryptographic sign-off from the Data Governance Steward (Ansh).
* **`DENIED`**: Request constitutionally prohibited; connection refused with fail-closed refusal artifact logged.

---

## 2. Complete Constitutional Access Control Matrix

The following matrix governs all interactions across the BHIV VANA / MASTERDB platform:

| # | Actor / Consumer Identity | Role | Target Dataset | Dataset Classification | Environment | Declared Purpose | READ | WRITE | MODIFY | DELETE | EXPORT | ADMIN | Governed Decision | Constitutional Gate Rule |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **01** | **VANA UI / FIN Dashboard** | Approved Consumer | `DS-FSI-ISFR-2023-FOREST-COVER` | `CANONICAL` | Production | District & State Canopy Visualization | **YES** | **NO** | **NO** | **NO** | Controlled | **NO** | **`ALLOWED`** | G-RULE-01: Approved consumer reading canonical data for declared visualization purpose. |
| **02** | **VANA UI / FIN Dashboard** | Approved Consumer | `DS-THANECREEK-2023-BIOMASS` | `CANONICAL_ECOSYSTEM` | Production | Mangrove Spatial Biomass Mapping | **YES** | **NO** | **NO** | **NO** | Controlled | **NO** | **`ALLOWED`** | G-RULE-01: Validated ecosystem ground-truth access for approved UI mapping. |
| **03** | **AIAIC Platform** | Approved Consumer | `DS-FSI-ISFR-2023-FOREST-COVER` | `CANONICAL` | Production | Agricultural Impact Analysis | **YES** | **NO** | **NO** | **NO** | Controlled | **NO** | **`ALLOWED`** | G-RULE-02: Inter-platform consumer reading approved public canonical records. |
| **04** | **Carbon Intelligence Engine** | Analytical Consumer | `DS-THANECREEK-2023-BIOMASS` | `CANONICAL_ECOSYSTEM` | Production | Blue Carbon Stock Quantification | **YES** | **NO** | **NO** | **NO** | **YES** | **NO** | **`ALLOWED`** | G-RULE-03: Analytical engine permitted read & export of derived carbon calculations. |
| **05** | **Carbon Intelligence Engine** | Analytical Consumer | `DS-THANECREEK-2023-BIOMASS` | `CANONICAL_ECOSYSTEM` | Production | Unspecified / General Ingestion | **NO** | **NO** | **NO** | **NO** | **NO** | **NO** | **`DENIED`** | G-RULE-04: Purpose limitation violation; purpose must be explicit and registered. |
| **06** | **Group 3 Field Pipeline** | Ingestion Producer | `DS-GROUP3-TC-Z03-F02` | `SOURCE_OBSERVATION` | Production | Raw Drone Sensor Ingestion | **YES** | **YES** | Controlled | **NO** | **NO** | **NO** | **`ALLOWED`** | G-RULE-05: Ingestion pipeline permitted to write source observations via schema validator. |
| **07** | **Group 3 Field Pipeline** | Ingestion Producer | `DS-FSI-ISFR-2023-FOREST-COVER` | `CANONICAL` | Production | Ad-hoc Modification of Government Stats | **NO** | **NO** | **NO** | **NO** | **NO** | **NO** | **`DENIED`** | G-RULE-06: Producers cannot alter statutory datasets owned by external authorities. |
| **08** | **FSI Dataset Steward** | Dataset Owner | `DS-FSI-ISFR-2023-FOREST-COVER` | `CANONICAL` | Production | Annual Baseline Verification & Update | **YES** | Controlled | **YES** | **NO** | Controlled | **NO** | **`ALLOWED`** | G-RULE-07: Owner may append versioned updates; destructive in-place overwrite forbidden. |
| **09** | **MDU Semantic Engine (Nupur)**| Semantic Validator | All Registered Datasets | Any | Any | Schema & Ontology Verification | **YES** | **NO** | **NO** | **NO** | **NO** | **NO** | **`ALLOWED`** | G-RULE-08: MDU has universal read for semantic validation, zero write/mutation authority. |
| **10** | **TANTRA Runtime (Rajaryan)** | Execution Authority | All Governed Datasets | `CANONICAL`, `SOURCE` | Production | Runtime Policy Gate Enforcement | **YES** | **NO** | **NO** | **NO** | **NO** | **NO** | **`ALLOWED`** | G-RULE-09: TANTRA verifies state during /vana/execute; does not mutate MasterDB tables. |
| **11** | **Bucket Service (Siddhesh)** | Evidence Connector | `raw_artifact` / Evidence Rows | `EVIDENCE` | Production | Parent Hash Chain & Artifact Storage | **YES** | **YES** | **NO** | **NO** | **NO** | **NO** | **`ALLOWED`** | G-RULE-10: Bucket append-only writer for hashes and storage refs; immutability enforced. |
| **12** | **Pravah Operational Health** | Monitoring Daemon | Health & Processing Run Tables | `RUNTIME` | Production | Queue Latency & Run Status Checks | **YES** | **NO** | **NO** | **NO** | **NO** | **NO** | **`ALLOWED`** | G-RULE-11: Telemetry daemon limited to telemetry and processing_run tables. |
| **13** | **InsightFlow Observability** | Audit Collector | Provenance & Processing Runs | `EVIDENCE`, `RUNTIME` | Production | Distributed Trace Visualisation | **YES** | **NO** | **NO** | **NO** | Controlled | **NO** | **`ALLOWED`** | G-RULE-12: Read-only access to audit logs and traceparent metadata. |
| **14** | **MASTERDB Platform Admin (Kavy)**| Platform Operator | System Catalog & DB Tables | All | Staging / Prod | Operational Maintenance, Index Tuning | Controlled | Controlled | Controlled | Controlled | Controlled | **YES** | **`CONTROLLED`** | G-RULE-13: Full DDL/DBA authority; data modifications logged in immutable audit ledger. |
| **15** | **Governance Lead (Ansh)** | Constitutional Steward| All Catalog & Access Rules | All | All | Governance Auditing, Quarantine Review| **YES** | Controlled | Controlled | Controlled | Controlled | Controlled | **`ALLOWED`** | G-RULE-14: Governance steward manages classifications, access rules, and quarantine triage. |
| **16** | **External Commercial Partner** | External Consumer | `DS-FSI-ISFR-2023-FOREST-COVER` | `CANONICAL` | Production | Bulk Data Exfiltration / Resale | **NO** | **NO** | **NO** | **NO** | **NO** | **NO** | **`DENIED`** | G-RULE-15: Commercial bulk exfiltration prohibited under government open terms. |
| **17** | **External Research University** | Academic Partner | `DS-THANECREEK-2023-BIOMASS` | `CANONICAL_ECOSYSTEM` | Staging / Prod | Peer Research Replication | **YES** | **NO** | **NO** | **NO** | Controlled | **NO** | **`REQUIRES_APPROVAL`** | G-RULE-16: External sharing requires Data Sharing Agreement (DSA) & Ansh sign-off. |
| **18** | **Unregistered / Unknown App** | Unknown | Any Dataset | Any | Production | Unknown / Probing | **NO** | **NO** | **NO** | **NO** | **NO** | **NO** | **`DENIED`** | G-RULE-17: Fail-Closed. Unauthenticated/unregistered identity immediately blocked & alerted.|
| **19** | **Internal Developer Daemon** | Developer | Production MasterDB | `CANONICAL` | Development | Debugging / Scratch Experimentation | **NO** | **NO** | **NO** | **NO** | **NO** | **NO** | **`DENIED`** | G-RULE-18: Development code cannot touch production MasterDB; must use mock or staging DB. |
| **20** | **CI/CD Automated Test Runner** | Automated Agent | `DS-SYNTHETIC-GROUP3-FIXTURE` | `FIXTURE` | Test / CI | Automated Regression Verification | **YES** | **YES** | **YES** | **YES** | **NO** | **NO** | **`ALLOWED`** | G-RULE-19: Fixtures isolated to ephemeral test environment; cannot cross into production. |
| **21** | **Security / Compliance Auditor**| Independent Auditor | MasterDB Audit Ledger & Prov | `EVIDENCE` | Production | Regulatory Compliance Proof Verification| **YES** | **NO** | **NO** | **NO** | Controlled | **NO** | **`ALLOWED`** | G-RULE-20: Read-only cryptographic inspection of lineage and idempotency tables. |

---

## 3. Detailed Operational Access Scenarios

### Scenario 1: Approved Consumer Request (Allowed Path)
* **Caller:** `VANA UI Service` (`X-Product-Id: VANA`, `X-Consumer-Role: APPROVED_CONSUMER`)
* **Request:** `GET /official/forest-cover/FC-9e602eff084ffc653d5bab7e0cfc6c52`
* **Purpose Header:** `X-Purpose: DISTRICT_CANOPY_ANALYSIS`
* **Environment:** Production
* **Evaluation:**
  1. Identity verified in whitelist: **PASS**.
  2. Dataset classification is `CANONICAL`: **PASS**.
  3. Purpose matches intended use in dataset profile: **PASS**.
  4. Action is `READ`: **PASS**.
* **Result:** **`HTTP 200 OK`** with structured canonical record and provenance trace.

### Scenario 2: Direct Database Port Access Attempt (Blocked Path)
* **Caller:** Developer laptop running `psql -h 163.128.209.18 -U postgres`
* **Request:** Direct TCP connection to PostgreSQL port `5432`
* **Evaluation:**
  1. Direct database access bypasses API authentication and governance middleware.
  2. Constitutional Rule: MASTERDB must not allow un-proxied client connections.
* **Result:** **`TCP CONNECTION REFUSED / BLOCKED BY FIREWALL`**. All interaction must route through the MasterDB FastAPI gateway (`port 8013`).

### Scenario 3: Bulk Export Request by External App (Blocked Exfiltration)
* **Caller:** `PartnerService-Alpha`
* **Request:** `GET /observations/export?format=csv&limit=1000000`
* **Purpose Header:** `X-Purpose: COMMERCIAL_DATA_SYNC`
* **Evaluation:**
  1. Role is `EXTERNAL_CONSUMER`.
  2. Dataset contains `CANONICAL` and `RESTRICTED` records.
  3. Action is `EXPORT` with commercial intent.
  4. No active Data Sharing Agreement on file.
* **Result:** **`HTTP 403 FORBIDDEN`** (`ERR_UNAUTHORIZED_EXPORT_PURPOSE`). Constitutional security event logged to Bucket evidence chain.

### Scenario 4: Ingestion of Unverified Fixture into Production (Quarantined)
* **Caller:** `Group3-Scout-Daemon`
* **Request:** `POST /observations` with `synthetic_state: "SYNTHETIC"` but `dataset_id: "DS-THANECREEK-2023-BIOMASS"`
* **Evaluation:**
  1. Ingestion payload marked synthetic while targeting a canonical physical dataset.
  2. Ground Rule Violation: Synthetic test data must never contaminate physical canonical datasets.
* **Result:** **`HTTP 422 UNPROCESSABLE ENTITY`**. Payload diverted to `QUARANTINE` store for governance audit.

---

## 4. Enforcement & Audit Specifications

1. **Gate Placement:** Access evaluation runs as pre-routing ASGI middleware on all MasterDB API endpoints.
2. **Audit Logging:** Every access evaluation (whether `ALLOWED`, `CONTROLLED`, or `DENIED`) generates a structured audit log containing:
   * `timestamp` (UTC ISO 8601)
   * `trace_id` (W3C Traceparent)
   * `actor_identity`
   * `target_dataset_id`
   * `declared_purpose`
   * `action`
   * `governance_decision`
   * `rule_code`
3. **Fail-Closed Guarantee:** If the Policy DB or Governance Engine becomes unreachable, the middleware defaults to **`DENIED`** (`HTTP 503 SERVICE UNAVAILABLE - GOVERNANCE_OFFLINE`).

---

## 5. Review & Approval Sign-Off

**Enacted and Enforced by:**  
*Ansh (Data Governance Lead)*  
*Kavy (MASTERDB Platform Lead)*  
*Rajaryan (TANTRA Runtime Authority Lead)*  
