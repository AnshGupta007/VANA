# MASTERDB GOVERNANCE & CONSTITUTIONAL CONTROL MODEL

**Document Identifier:** MASTERDB-GOV-MODEL-V1.0  
**Candidate / Owner:** Ansh (Data Governance & Constitutional Controls)  
**Collaborating Platform Lead:** Kavy (MASTERDB Platform Owner)  
**Dependencies:** MDU / Nupur (Semantics & Meaning), TANTRA / Rajaryan (Runtime Authority), Bucket / Siddhesh (Evidence & Lineage), Pravah / Shivam (Operational Health), InsightFlow / Vijay & Harsha (Observability)  
**Mode:** Learn → Inspect → Classify → Govern → Prove  
**Target Environment:** BHIV Governed Data Platform / VANA Ecosystem  
**Date:** September 2026  

---

## 1. Executive Summary & Core Mission

Ansh’s mission is to establish the authoritative governance and constitutional control layer around **MASTERDB** while working directly with Kavy.

The central objective is to ensure MASTERDB becomes the central governed data platform for BHIV, without mutating into an uncontrolled "God database" containing everything, accessible to everyone, for every purpose.

### The Governing Principle

> **"MASTERDB can centralize governed data access without centralizing unrestricted authority."**

MASTERDB is an infrastructure platform for storing and retrieving structured records under strict control contracts. It is **not** the semantic dictator of BHIV, **not** the business policy decider, **not** the runtime enforcement engine, and **not** an open data lake where unvalidated dumps reside.

Ansh owns the rules, boundaries, and validation gates governing:
* What data is allowed into MASTERDB
* How it is classified
* Who owns it and who custodies it
* Who may access it, under what identity, role, and purpose
* Under what environmental conditions and actions
* How long it may exist (retention and deprecation)
* What can be shared across consumers
* What must remain strictly restricted or quarantined
* What must never be treated as canonical

---

## 2. First Principle: Constitutional Separation of Concerns

BHIV operates on the foundational constitutional axiom:

$$\text{One System} \neq \text{One Authority}$$

The governance architecture strictly decouples data platform mechanics, semantic meaning, evidence persistence, runtime authority, and constitutional oversight:

```
                            BHIV ECOSYSTEM
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │      GOVERNANCE       │
                      │     ANSH (Group 4)    │
                      │ Rules, Controls, Gates│
                      └───────────┬───────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          ▼                       ▼                       ▼
      ┌─────────┐           ┌───────────┐           ┌───────────┐
      │   MDU   │           │ MASTERDB  │           │  TANTRA   │
      │ (Nupur) │           │  (Kavy)   │           │(Rajaryan) │
      │ Meaning │           │ Governed  │           │  Runtime  │
      │ Semantics           │   Data    │           │ Authority │
      └────┬────┘           └─────┬─────┘           └─────┬─────┘
           │                      │                       │
           └──────────────┬───────┘                       │
                          ▼                               ▼
                    ┌───────────┐                   ┌───────────┐
                    │  Bucket   │                   │  Pravah & │
                    │(Siddhesh) │                   │InsightFlow│
                    │ Evidence  │                   │Telemetry &│
                    │ & Lineage │                   │   Health  │
                    └───────────┘                   └───────────┘
```

### Clarification of System Responsibilities

| Subsystem | Primary Custodian | Core Role | What It Controls | What It Must NEVER Control |
| :--- | :--- | :--- | :--- | :--- |
| **Governance** | **Ansh** | Constitutional Control | Policy boundaries, dataset classifications, access matrices, purpose constraints, lifecycle transitions | Storing raw physical bytes; executing business algorithms; inventing raw schemas |
| **MASTERDB** | **Kavy** | Governed Data Platform | Canonical storage, primary key references, spatial geometries, indexed fast retrieval APIs | Semantic definitions; runtime business decisions; granting unilateral access |
| **MDU** | **Nupur** | Semantic Authority | Field definitions, scientific ontology, schema validations, contextual meaning, domain terms | User access rights; platform storage topology; data retention infrastructure |
| **TANTRA** | **Rajaryan** | Runtime Authority | Execution gates, runtime token verification, policy evaluation middleware, fail-closed enforcement | Data persistence; schema definition; bypassing MasterDB retrieval rules |
| **Bucket** | **Siddhesh** | Evidence & Lineage | Append-only hash chains, raw sensory artifacts, cryptographic verification blocks | Ingest-time classification; real-time transactional filtering |
| **Pravah** | **Shivam** | Operational Health | Circuit breakers, pipeline health, queue latency, throughput monitoring | Data access decisions; governance rulings |
| **InsightFlow** | **Vijay / Harsha** | Observability & Audit | W3C distributed traces, execution audit trails, visual telemetry | Modifying records; overriding governance gates |

Ansh does **not** become the owner of the data itself. He owns the rules, gate policies, and control boundaries governing its entire lifecycle.

---

## 3. Authority Boundaries: "May" vs "Must Not"

To prevent authority creep, the boundaries of MASTERDB are constitutionally locked:

### MASTERDB May:
1. **Register governed datasets** that possess an authenticated owner, verified source, and approved MDU schema reference.
2. **Store and reference data points** with explicit spatial geometries (EPSG:4326), timestamps, and measurement units.
3. **Expose approved data** strictly through authenticated, authorized REST and programmatic interfaces.
4. **Track ownership and custodianship** metadata for every cataloged asset.
5. **Track complete lineage and provenance**, linking every measurement back to its raw source and processing run.
6. **Apply access policies** based on caller identity, role, and declared purpose.
7. **Track dataset lifecycle states** (from Discovered to Archived).
8. **Provide deterministic, controlled retrieval** with guaranteed idempotency and audit logs.

### MASTERDB Must Not:
1. **Invent semantic meaning**: MASTERDB cannot redefine what `canopy_height` or `above_ground_biomass` means; that belongs exclusively to MDU.
2. **Decide business policy**: MASTERDB cannot determine whether a carbon credit should be issued or denied; that belongs to downstream decision engines and TANTRA.
3. **Override MDU schemas**: MASTERDB cannot store fields that violate registered MDU validation contracts.
4. **Execute workflows**: MASTERDB is not an orchestrator; it does not trigger external drones, field missions, or payment transfers.
5. **Become the evidence authority**: Raw sensor outputs (LAS files, raw drone video) belong in Bucket; MASTERDB holds references and content hashes, not raw evidence authority.
6. **Grant unrestricted access**: No direct database connections (`psql`, direct port access) may bypass API governance layers.
7. **Automatically declare everything canonical**: Ingested data is never canonical by default; it requires explicit verification, provenance, and validation.
8. **Become a universal data dump**: Untracked, unclassified, or unowned data dumps are strictly rejected at the ingestion boundary.

---

## 4. Dataset Classification Model

Every dataset registered or ingested into the MASTERDB ecosystem must be assigned an explicit classification. Defaulting to canonical or production status is prohibited.

```
                         [ INCOMING DATA ]
                                 │
                     Can provenance/owner/MDU
                       schema be established?
                                 │
                ┌────────────────┴────────────────┐
               YES                                NO
                │                                 │
                ▼                                 ▼
   What is the intended usage?               [ UNKNOWN ]
        │                                         │
        ├─ Authoritative Governed ──> [ CANONICAL ]  ▼
        ├─ Original Source Raw ─────> [ SOURCE ]    [ QUARANTINED ]
        ├─ Computed / Aggregated ───> [ DERIVED ]    (Isolated / No
        ├─ Lab / Research Only ─────> [ EXPERIMENTAL ] Consumer Access)
        ├─ Testing / Mock ──────────> [ FIXTURE ]
        ├─ Raw Verification Hash ───> [ EVIDENCE ]
        ├─ Ephemeral System State ──> [ RUNTIME ]
        ├─ Regulated / Confidential ─> [ RESTRICTED ]
        └─ Proprietary Algorithms ──> [ PRIVATE/IP ]
```

### Classification Taxonomy

| Classification | Meaning & Intent | Permitted Consumers | Retention Rule | Canonical Eligibility |
| :--- | :--- | :--- | :--- | :--- |
| **CANONICAL** | Authoritative, fully validated, governed dataset of record for BHIV. | All authenticated & authorized consumers with approved purpose. | Long-term governed; immutable versioning. | **YES** (Already Canonical) |
| **SOURCE** | Original, unmodified source material (e.g., FSI ISFR PDF extract, raw Open-Meteo response). | Data engineers, pipeline workers, audit systems. | Retained per source agreement; immutable. | **NO** (Must be transformed & validated) |
| **DERIVED** | Calculated, aggregated, or transformed data generated from one or more parent datasets. | Permitted application consumers. | Linked to parent lifecycle. | **CONDITIONAL** (If derivation methodology is certified) |
| **EXPERIMENTAL** | Non-production research datasets, trial algorithms, or exploratory scientific models. | Research team, model developers. | 90 days default unless renewed. | **NO** |
| **FIXTURE** | Synthetic or mock test data generated strictly for automated CI/CD and verification. | CI/CD pipelines, unit/integration test runners. | Ephemeral; destroyed on build completion. | **STRICTLY PROHIBITED** |
| **EVIDENCE** | Immutable cryptographic audit record, parent hash block, or sensory verification token. | TANTRA, Bucket, Auditor, Legal. | Permanent / WORM (Write Once Read Many). | **NO** (Evidence of fact, not dataset) |
| **RUNTIME** | Ephemeral system state, health metrics, session locks, and temporary cache data. | Operational daemons, Pravah, internal services. | Ephemeral (hours to days). | **NO** |
| **RESTRICTED** | Sensitive dataset requiring elevated clearance, legal approval, or explicit consent. | Named consumers with explicit governance grant. | Encrypted; access logged per read. | **CONDITIONAL** (May be canonical within restricted boundary) |
| **PRIVATE/IP** | Proprietary internal algorithms, trade secrets, patented allometric equations. | Core IP authorized personnel only. | Highly restricted; no external export. | **NO** |
| **QUARANTINED** | Data suspected of corruption, unverified provenance, schema drift, or license breach. | Governance team (Ansh) & Security triage only. | 30-day quarantine hold before purge or cure. | **PROHIBITED** |
| **UNKNOWN** | Classification, provenance, or ownership has not yet been established. | **NONE** (Blocked from all read/write paths). | Immediate escalation; defaults to quarantine. | **PROHIBITED** |

### Constitutional Rule on UNKNOWN and QUARANTINED
> **UNKNOWN and QUARANTINED are valid, first-class states.**  
> If provenance, ownership, schema conformity, or licensing rights cannot be proven, the governance system must **refuse** canonical designation and place the record into `UNKNOWN` or `QUARANTINED`. Falsely classifying unverified data as `CANONICAL` to make pipelines pass is a severe constitutional violation.

---

## 5. Data Ownership & Custodianship Framework

A dataset residing within MASTERDB does not imply that MASTERDB owns the data. Ownership resides with the producing domain or authorizing institutional authority.

### The 7 Mandatory Ownership Questions
For every registered dataset, governance must definitively record:

1. **WHO PRODUCED IT?** (Author, sensor operator, remote-sensing satellite, or lab technician).
2. **WHO OWNS IT?** (Institutional authority, government publisher, legal entity, or BHIV domain lead).
3. **WHO CUSTODIES IT?** (The operational team responsible for its platform health, storage, and security in MASTERDB).
4. **WHO MAY USE IT?** (Whitelisted applications, products, and partner entities).
5. **WHO MAY MODIFY IT?** (Explicit authorized update authorities; canonical records are append-only/versioned).
6. **WHO MAY EXPORT IT?** (Entities legally and constitutionally permitted to extract data outside BHIV).
7. **WHO APPROVES ITS USE?** (The governance authority or data steward designated to grant new access grants).

### Minimum Governance Metadata Schema
Every dataset registered in MASTERDB must carry the following immutable metadata block:

```json
{
  "dataset_id": "DS-FSI-ISFR-2023-FOREST-COVER",
  "dataset_name": "India State of Forest Report 2023 Forest Cover",
  "owner": "Forest Survey of India / MoEFCC, Govt of India",
  "custodian": "Kavy (MasterDB Platform Lead)",
  "governance_steward": "Ansh (Data Governance Lead)",
  "source": {
    "source_id": "SRC-FSI-ISFR-2023",
    "source_type": "GOVERNMENT_DATASET",
    "publisher": "Forest Survey of India",
    "url": "http://fsi.nic.in/uploads/isfr2023/isfr_book_eng-vol-1_2023.pdf",
    "citation": "India State of Forest Report 2023, Volume I, ISBN 978-81-950073-9-4",
    "retrieved_at": "2026-09-03T05:48:00Z",
    "is_synthetic": false
  },
  "source_authority": "Ministry of Environment, Forest and Climate Change, Govt of India",
  "classification": "CANONICAL",
  "sensitivity": "PUBLIC_GOVERNMENT_OPEN",
  "mdu_schema_ref": "mdu://ontology/environmental/v2.2/forest_cover.schema.json",
  "access_policy": "POLICY-GOV-OPEN-CONSUMERS-V1",
  "allowed_consumers": ["VANA", "FIN", "AIAIC", "PRAVAH", "RESEARCH_CORE"],
  "intended_use": "Macro-level district and state environmental baseline carbon & canopy analysis",
  "retention_policy": "PERMANENT_HISTORICAL_VERSIONED",
  "lifecycle_status": "ACTIVE",
  "approval_authority": "Ansh / BHIV Data Governance Council"
}
```

---

## 6. Access & Purpose Control Framework

Authentication (who you are) is insufficient. Authorization must incorporate dataset classification, operational context, environment, and declared **purpose**.

### The 6-Tuple Access Evaluation Rule

$$\text{Decision} = f(\text{Identity}, \text{Role}, \text{Classification}, \text{Purpose}, \text{Environment}, \text{Action})$$

```
  ┌───────────────┐
  │   IDENTITY    │ ── (App ID, Service Principal, User ID)
  └───────┬───────┘
          │
  ┌───────▼───────┐
  │     ROLE      │ ── (Consumer, Steward, Admin, Auditor)
  └───────┬───────┘
          │
  ┌───────▼───────┐
  │ CLASSIFICATION│ ── (Canonical, Source, Restricted, Fixture...)
  └───────┬───────┘    ════> [ GOVERNANCE POLICY EVALUATION ] ════> DECISION
          │                                                          (ALLOWED /
  ┌───────▼───────┐                                                  DENIED /
  │    PURPOSE    │ ── (District Analysis, Verification, Export)     RESTRICTED)
  └───────┬───────┘
          │
  ┌───────▼───────┐
  │  ENVIRONMENT  │ ── (Production, Staging, Development)
  └───────┬───────┘
          │
  ┌───────▼───────┐
  │    ACTION     │ ── (READ, WRITE, MODIFY, DELETE, EXPORT, ADMIN)
  └───────────────┘
```

### Action Definitions
* **READ**: Retrieve data records for authorized computation.
* **WRITE**: Ingest new observation or measurement records.
* **MODIFY**: Append versioned modifications or corrections (destructive in-place updates are blocked for canonical data).
* **DELETE**: Deactivate, soft-delete, or archive records under retention schedules.
* **EXPORT**: Transmit datasets outside the BHIV boundary to third parties or disk bundles.
* **ADMIN**: Alter schema migrations, create indexes, register datasets, or manage connection parameters.

### Concrete Scenarios

#### Scenario A: Legitimate Internal Consumer
* **Application:** AIAIC
* **Dataset:** `DS-FSI-ISFR-2023-FOREST-COVER` (Classification: CANONICAL)
* **Role:** Approved Consumer
* **Purpose:** District Forest Degradation Analysis
* **Environment:** Production
* **Action:** READ
* **Decision:** **`ALLOWED`**

#### Scenario B: Unapproved Purpose / Exfiltration Attempt
* **Application:** AIAIC
* **Dataset:** `DS-FSI-ISFR-2023-FOREST-COVER` (Classification: CANONICAL)
* **Role:** Approved Consumer
* **Purpose:** External Commercial Bulk Sale (Unapproved Purpose)
* **Environment:** Production
* **Action:** EXPORT
* **Decision:** **`BLOCKED`** (Purpose mismatch; requires explicit Data Steward export permit)

#### Scenario C: Unknown Consumer
* **Application:** UNREGISTERED_DAEMON_99
* **Dataset:** `DS-THANECREEK-2023-BIOMASS` (Classification: RESTRICTED)
* **Role:** Unknown
* **Purpose:** None Declared
* **Environment:** Production
* **Action:** READ
* **Decision:** **`BLOCKED & LOGGED`** (Fail-closed; security alert emitted)

---

## 7. Lifecycle Governance Model

Datasets must pass through deterministic lifecycle states. Datasets do not remain active indefinitely without periodic re-certification.

```
       [ DISCOVERED ]
             │
             ▼
       [ CLASSIFIED ]
             │
             ▼
        [ VALIDATED ] ◄───────────────────┐
             │                            │
             ▼                            │
       [ REGISTERED ]                     │
             │                            │
             ▼                            │ (Remediation)
          [ ACTIVE ]                      │
             │                            │
             ├──────> [ UPDATED / VERSIONED ]
             │                            │
             ▼                            │
        [ DEPRECATED ]                    │
             │                            │
             ▼                            │
         [ ARCHIVED ]                     │
             │                            │
             ▼                            │
         [ PURGED ]                       │
                                          │
       [ UNKNOWN / DRIFT ]                │
             │                            │
             ▼                            │
       [ QUARANTINED ] ───────────────────┘
```

### Lifecycle Stage Specifications

1. **DISCOVERED**: Raw dataset or external source identified by ingestion scouts or scientific partners. Not queryable.
2. **CLASSIFIED**: Initial classification, sensitivity level, and owner assigned by Governance (Ansh).
3. **VALIDATED**: Schema verified by MDU; scientific allometry, coordinate bounding boxes, and units validated.
4. **REGISTERED**: Formal registration in MASTERDB catalog with unique `dataset_id` and provenance tracking records.
5. **ACTIVE**: Available for production query consumption by authorized callers.
6. **UPDATED / VERSIONED**: New observation cycle or methodology released. Superseded versions are marked deprecated, preserving historical immutability.
7. **DEPRECATED**: Sunset notice issued. No new pipelines may bind to this dataset. Existing pipelines given 90 days migration window.
8. **ARCHIVED**: Retained in cold storage/Bucket for legal and audit replay. Inactive in live query caches.
9. **PURGED**: Destroyed according to data retention schedules if contractually required.
10. **QUARANTINED**: Isolated immediately upon detection of schema drift, unverified coordinates, or invalid license.

### Prevention of "Digital Archaeology"
Without explicit lifecycle enforcement, dead projects leave zombie tables that subsequent developers treat as gospel. MASTERDB enforces:
* Mandatory 180-day lifecycle review for all non-statutory datasets.
* Automated warning flags when an active dataset has had zero reads or updates in 12 months.
* Deprecation schedules tied to source publisher updates (e.g., FSI ISFR reports update biannually).

---

## 8. Canonical vs Non-Canonical Governance Rules

A dataset does **not** become CANONICAL merely because it is stored in MasterDB or because a developer pushed it to production.

### The 10 Gate Requirements for CANONICAL Status

| Gate # | Requirement | Validation Standard | Failure Action |
| :---: | :--- | :--- | :--- |
| **G1** | **Known Owner** | Explicit named entity or institution with operational accountability. | Retain as SOURCE / UNKNOWN |
| **G2** | **Known Source** | Authenticated publisher URL, DOI, or physical report ISBN. | Reject Ingestion |
| **G3** | **Known Provenance** | Unbroken transformation chain from raw bytes to stored record. | Classify as DERIVED_UNVERIFIED |
| **G4** | **Valid Schema** | 100% adherence to MDU registered JSON/SQL schema. | Quarantine immediately |
| **G5** | **MDU Compatibility** | Semantic terms match MDU ontology dictionary (no bespoke ad-hoc columns). | Reject Ingestion |
| **G6** | **Quality Validation** | Ground truth verification, boundary checks, and range plausibility tests. | Mark as UNVERIFIED |
| **G7** | **Appropriate Access Policy** | Defined allowed consumers, roles, and allowed purposes. | Block production reads |
| **G8** | **Integrity Verification** | SHA-256 fingerprint matching idempotency registry. | Quarantine on collision |
| **G9** | **Lifecycle Defined** | Active status with explicit retention and versioning policy. | Block Registration |
| **G10** | **Approved Authority** | Sign-off by Data Governance Lead (Ansh) and Platform Lead (Kavy). | Staging hold |

If any of these 10 criteria cannot be demonstrated with hard evidence, the dataset remains:
$$\text{SOURCE} \mid \text{DERIVED} \mid \text{EXPERIMENTAL} \mid \text{QUARANTINED} \mid \text{UNKNOWN}$$

---

## 9. Preventing the "God Database"

The most dangerous anti-pattern in enterprise data engineering is the **God Database**: a central monolithic store where every application dumps raw data, bypasses business logic, executes untracked mutations, and grants root database credentials to every microservice.

### The 10 Red Flags of Authority Drift

1. **Direct Production DB Access**: Developers or external microservices connecting directly to PostgreSQL port `5432` rather than through the governed API.
2. **Applications Bypassing APIs**: Services reading SQLite files directly off the disk or mounting volume storage out-of-band.
3. **Unknown Datasets Marked Canonical**: Ingestion scripts stamping `status='VALIDATED'` without passing MDU or governance gates.
4. **Missing Ownership Metadata**: Rows in the `dataset` table having `NULL` or generic `"system"` owner values.
5. **Missing Purpose in Requests**: API retrieval requests that do not supply a mandatory `X-Purpose` or contextual header.
6. **Unrestricted Bulk Exports**: Endpoints permitting un-paginated, unfiltered dumps of raw records without audit logging.
7. **Semantic Rules Inside MASTERDB**: Stored procedures or triggers implementing domain science formulas (e.g. allometric biomass calculations inside database functions).
8. **Business Decisions Inside MASTERDB**: MasterDB returning approved/denied credits or financial rulings rather than raw physical observations.
9. **Application-Specific Governance Embedded in Core**: Hardcoding UI layout rules or client-specific flags into core relational schemas.
10. **Absence of Retention / Deletion Rules**: Datasets persisting indefinitely with no deprecation schedule or audit trails.

### The 5 Classic God Database Traps & Preventive Controls

```
┌─────────────────────────────────┬─────────────────────────────────┬─────────────────────────────────┐
│     God Database Anti-Pattern   │          Operational Risk       │       Preventive Control        │
├─────────────────────────────────┼─────────────────────────────────┼─────────────────────────────────┤
│ 1. Universal Data Dumping Ground│ Schema drift, garbage data, lost│ Hard gate at API ingestion:     │
│    (Anything can be POSTed)     │ provenance, unvalidated mocks.  │ reject unclassified/unregistered│
│                                 │                                 │ datasets (HTTP 422 Unprocessable│
├─────────────────────────────────┼─────────────────────────────────┼─────────────────────────────────┤
│ 2. Bypass of Meaning / MDU      │ Mismatched units, disputed terms│ MDU schema validator runs       │
│    (Schema defined ad-hoc)      │ ("height" in cm vs m).          │ ahead of MasterDB persistence;  │
│                                 │                                 │ terms must exist in ontology.   │
├─────────────────────────────────┼─────────────────────────────────┼─────────────────────────────────┤
│ 3. God Administrator Credentials│ Single leak compromises all     │ DB credentials locked to API    │
│    (Shared superuser passwords) │ partitions, audits, and data.   │ gateway; apps use scoped tokens │
│                                 │                                 │ with role + purpose checks.     │
├─────────────────────────────────┼─────────────────────────────────┼─────────────────────────────────┤
│ 4. Hidden Copies & Split Truth  │ Inconsistent versions; digital  │ Idempotency key registry;       │
│    (Rogue local CSV/SQLite sync)│ archaeology across branches.    │ canonical records have global   │
│                                 │                                 │ UUIDs + parent hashes.          │
├─────────────────────────────────┼─────────────────────────────────┼─────────────────────────────────┤
│ 5. Embedded Decision Logic      │ Database becomes bottleneck;    │ MasterDB only returns governed  │
│    (DB decides business policy) │ cannot change business doctrine │ observations; decision engine   │
│                                 │ without DB migration.           │ sits in TANTRA runtime layer.   │
└─────────────────────────────────┴─────────────────────────────────┴─────────────────────────────────┘
```

---

## 10. Collaboration With MDU (Semantics vs Governance)

The boundary between Nupur (MDU) and Ansh (Governance) is clean and non-overlapping:

* **MDU (Nupur) dictates MEANING:**  
  * *"What is this field?"*  
  * *"What does `above_ground_biomass` mean?"*  
  * *"What are the valid units (`Mg/ha`, `kg/m2`)?"*  
  * *"What is the valid mathematical range for Avicennia marina canopy height?"*
* **Governance (Ansh) dictates USAGE:**  
  * *"Who is permitted to read this biomass dataset?"*  
  * *"For what authorized purpose may it be read?"*  
  * *"Is this specific dataset instance CANONICAL or EXPERIMENTAL?"*  
  * *"How long is this dataset valid before it must be re-surveyed?"*
* **MASTERDB (Kavy) executes STORAGE & RETRIEVAL:**  
  * *"Here is the indexed observation record matching the approved query."*

---

## 11. Governance of External Data

External data entering BHIV (such as FSI reports, Open-Meteo API readings, Sentinel satellite rasters, or peer-reviewed academic literature) must answer 10 External Governance Questions:

1. **Source Authority:** Is the publisher recognized (e.g., MoEFCC, NASA, Copernicus, Elsevier)?
2. **License & Terms:** Does the license permit storage, transformation, and internal reuse?
3. **Usage Rights:** Are there commercial or public dissemination restrictions?
4. **Collection Method:** How was the data gathered (remote sensing, physical field plot, weather station)?
5. **Provenance:** Can the original PDF, API URL, or raw file be cited and cryptographically verified?
6. **Refresh Frequency:** How often does the publisher release updates, and how are updates tracked?
7. **Permitted Consumers:** Who within BHIV is authorized to query this external data?
8. **Commercial / Public Restrictions:** Can derived carbon models be exposed publicly or only internally?
9. **Retention & Archival:** Must raw source extracts be archived in Bucket indefinitely?
10. **Derived-Data Rights:** Does BHIV retain rights to derived models generated from this data?

---

## 12. Kavy + Ansh Working Model

```
       KAVY (MASTERDB Platform)                  ANSH (Governance & Control)
  ┌───────────────────────────────────┐     ┌───────────────────────────────────┐
  │ • Builds and tunes the DB schema  │     │ • Defines classification standards│
  │ • Maintains PostgreSQL / SQLite   │     │ • Sets access & purpose policies  │
  │ • Implements indexing & query APIs│     │ • Evaluates canonical eligibility │
  │ • Ensures sub-second retrieval    │     │ • Audits gap closures & red flags │
  │ • Manages migrations & backups    │     │ • Enforces fail-closed boundaries │
  └─────────────────┬─────────────────┘     └─────────────────┬─────────────────┘
                    │                                         │
                    └───────────────────┬─────────────────────┘
                                        ▼
                         CONSTITUTIONAL COLLABORATION:
                         Platform + Constitutional Control
                                        │
                                        ▼
                         SAFE, GOVERNED DATA REUSE
                               ACROSS BHIV
```

* Kavy does not unilaterally invent governance policy or grant backdoor database permissions.
* Ansh does not unilaterally re-architect database indexes or break API schemas.
* They operate in tandem: **Platform Engineer + Constitutional Governor**.

---

## 13. Definition of Done & Sign-Off

This governance model is enacted and operational when:
1. All 11 dataset classifications are codified into active validation engines.
2. The 6-tuple access control rule is enforced on all retrieval and ingestion endpoints.
3. Every registered dataset carries an immutable governance profile answering the 7 ownership questions.
4. MDU schema validation is verified as a mandatory pre-condition to MasterDB storage.
5. All 10 God Database red flags are monitored with active preventive controls.

**Prepared and Submitted by:**  
*Ansh (Data Governance & Constitutional Controls Lead)*  

**Reviewed and Acknowledged by:**  
*Kavy (MASTERDB Platform Lead)*  
*Mohit (BHIV Integration Lead)*  
