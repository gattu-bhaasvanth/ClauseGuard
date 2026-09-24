# ClauseGuard: Project Master Plan

This document outlines the end-to-end multi-phase execution strategy and final delivery status for **ClauseGuard** — an AI-Powered Real-Estate Transaction Intelligence Platform with Cross-Document Discrepancy Detection.

---

## Guiding Principles & Engineering Standards

1. **Cross-Document Discrepancy First**: Individual document summaries are secondary; the primary engineering focus is identifying contradictions, omissions, and mismatched obligations across multiple transaction documents.
2. **Strict Informational Boundaries**: The system is an informational verification tool, not a licensed legal practitioner. Every finding must use calibrated terminology (*"Potential inconsistency detected"*, *"Potential risk"*, *"Requires manual verification"*) and never offer definitive legal advice.
3. **Traceability to Raw Evidence**: Every flag, metric, or identified discrepancy is traceable through an unbroken 5-tier audit chain: `Document -> Page -> Clause -> Statutory Benchmark -> Buyer Financial Exposure`.
4. **Honest ML Strategy**: No synthetic or pre-trained models are falsely claimed as custom-trained. The ML system was developed through rigorous curation of real statutory RERA clauses, provenance auditing, and empirical multi-candidate bake-off benchmarking with deterministic fallback.
5. **Modular Architecture**: Clean separation of concerns between UI presentation, document ingestion, clause parsing, metadata normalization, cross-document comparison, vector retrieval, and intelligent copilot orchestration.
6. **Zero External AI Lock-in**: Fully functional on local CPU environments with zero API keys or external inference costs required, using FastEmbed embeddings, SQLite, PyMuPDF, and scikit-learn.

---

## Roadmap Overview & Status

```
Phase 0: Project Foundation (Repository, Documentation & Environment)    [COMPLETED]
  │
Phase 1: Frontend Application Shell & Document Viewer                  [COMPLETED]
  │
Phase 2: Backend Architecture, Database & Core API Foundation          [COMPLETED]
  │
Phase 3: Robust Document Ingestion & OCR Processing Pipeline            [COMPLETED]
  │
Phase 4: Clause Intelligence Engine (Segmentation & Taxonomy)          [COMPLETED]
  │
Phase 5: Transaction Entity & Metadata Extraction Engine               [COMPLETED]
  │
Phase 6: Cross-Document Intelligence & Inconsistency Detector          [COMPLETED]
  │
Phase 7: Transaction Risk Analysis & Audit Report Engine               [COMPLETED]
  │
Phase 8: Grounded Transaction RAG & Semantic Exploration               [COMPLETED]
  │
Phase 9: Domain-Specific Clause Intelligence & ML Enhancement          [COMPLETED]
  │
Phase 10: Transaction Intelligence Copilot                             [COMPLETED]
  │
Phase 11: Production Hardening, Security & Reliability                 [COMPLETED]
  │
Phase 12: Deployment & Portfolio Demo Experience                       [COMPLETED]
```

---

## Detailed Phase Delivery Breakdown

---

### Phase 0: Project Foundation
*Status: Completed*
- Established root directory scaffold (`frontend/`, `backend/`, `docs/`, `data/`, `tests/`, `scripts/`).
- Standardized `.gitignore` covering Python, Node.js, environment secrets, and binary caches.
- Created `.env.example` documenting all configuration keys without exposing secrets.
- Initialized Git repository, verified clean initial tracking, and drafted system architecture.

---

### Phase 1: Frontend Application Shell & Document Viewer
*Status: Completed*
- Next.js 14 (App Router) + TypeScript + Tailwind CSS design system with dark-mode aesthetic.
- Transaction project dashboard with bundle management and health score visualization.
- Split-screen Document Viewer powered by `PDF.js` with page navigation, zoom, and highlight overlays.
- Inconsistency Alert Drawer deep-linking findings directly to page coordinates.

---

### Phase 2: Backend Architecture, Database & Core API Foundation
*Status: Completed*
- FastAPI backend application setup with modular REST routing (`/api/v1`).
- Asynchronous database engine (`SQLAlchemy 2.0` with SQLite/PostgreSQL compatibility).
- Relational schema: `TransactionBundle`, `Document`, `DocumentPage`, `Clause`, `Finding`, and `ExtractedAttribute`.
- Pydantic v2 validation schemas and serializable response envelopes.

---

### Phase 3: Document Ingestion & OCR Processing Pipeline
*Status: Completed*
- High-performance digital text extraction using PyMuPDF (`fitz`).
- Page-level coordinate extraction, bounding box preservation, and text density checks.
- Document normalization service standardizing whitespace, headers, footers, and table columns.
- Support for background asynchronous processing of large multi-page PDF agreements.

---

### Phase 4: Clause Intelligence Engine
*Status: Completed*
- Regex and layout-informed clause boundary detection identifying articles, sections, and sub-clauses.
- 11-category statutory real-estate clause taxonomy (Possession, Payment, Area, Forfeiture, Alteration, Defects Liability, Force Majeure, Dispute, Compliance, Maintenance, General).
- Deterministic heuristic keyword weighting system establishing the reliable baseline.
- Obligation role tagging (Buyer, Developer, Mutual).

---

### Phase 5: Transaction Entity & Metadata Extraction
*Status: Completed*
- Structured entity extraction targeting property metrics (carpet area, super built-up area, tower, floor, unit).
- Financial obligation extractors (sale price, booking amounts, payment milestone breakdowns).
- Statutory identifier regex extractors for HARERA, MahaRERA, UP RERA registration numbers.
- Normalization of units (sq.ft, sq.m) and ISO 8601 timeline parameters.

---

### Phase 6: Cross-Document Intelligence & Inconsistency Detector
*Status: Completed*
- Cross-document alignment matrix correlating entities between brochures, allotment letters, and BBAs.
- Deterministic discrepancy evaluators:
  - *Carpet vs. Super Area discrepancies* (e.g. 1,450 sq.ft advertised vs. 1,380 sq.ft contracted).
  - *Possession timeline postponements* (e.g. June 2027 allotment vs. Dec 2027 + 180-day grace in BBA).
  - *Payment milestone summation vs. contract consideration discrepancies*.
- Evidence pairing engine linking primary and contradicting excerpts with exact page citations.

---

### Phase 7: Transaction Risk Analysis & Audit Report Engine
*Status: Completed*
- Asymmetric risk detection: flags 18% buyer default interest vs. nominal Rs. 5/sq.ft builder delay compensation.
- Unilateral layout alteration detection and aggressive earnest money forfeiture alerts.
- Transaction health scoring algorithm (0–100 scale).
- Informational Transaction Audit Report generator with print/export capabilities.

---

### Phase 8: Grounded Transaction RAG & Semantic Exploration
*Status: Completed*
- Hierarchy-preserving document chunker with clause and page metadata tags.
- Local vector embedding using `FastEmbed` (`BAAI/bge-small-en-v1.5`) running entirely on CPU.
- Cosine similarity vector retrieval with BM25 hybrid ranking.
- Strict citation grounding guardrails preventing hallucinations and citing document, page, and clause.

---

### Phase 9: Domain-Specific Clause Intelligence & ML Enhancement
*Status: Completed*
- Statutory dataset of 253 annotated real-estate clauses across 6 official Indian RERA sources with 100% provenance in `corpus_manifest.json`.
- Baseline evaluation established: Phase 4 keyword heuristics achieved 59.32% accuracy, 0.5720 Macro F1.
- Multi-candidate bake-off:
  - Candidate A (TF-IDF + Ridge Classifier): 0.5682 F1
  - Candidate B (FastEmbed Dense Head): 0.5684 F1
  - Candidate C (Semantic Prototype Manifold): 0.8788 Macro F1 (+30.51% accuracy jump, 0.030 ms latency).
- Production hybrid classifier: enforces confidence threshold (>= 0.60) with deterministic fallback.
- Full explainability UI: `ModelConfidenceBadge`, `ClassificationInspectorDrawer`, and `ModelDiagnosticsHub`.

---

### Phase 10: Transaction Intelligence Copilot
*Status: Completed*
- **Command Center**: Real-time cockpit displaying transaction health (74/100), quantified financial exposure (Rs. 25.65L), critical blockers, and action items.
- **Transaction Copilot**: Evidence-grounded conversational assistant with keyboard shortcut (`Cmd+K`), citation pills, and strict refusal contract for ungrounded questions.
- **Explainable Risk Intelligence**: 5-tier lineage drawer tracing Document -> Page -> Clause -> Statutory Benchmark -> Buyer Financial Exposure.
- **Intelligent Timeline**: Multi-document timeline classifying dates into 5 certainty states: `CONTRACTUAL`, `INFERRED`, `MARKETING`, `CONFLICTING`, `UNCERTAIN`.
- **Evidence Lineage Graph**: Visual dependency graph connecting findings to source document clauses.
- **Executive Transaction Brief**: Comprehensive 7-section printable memorandum.

---

### Phase 11: Production Hardening, Security & Reliability
*Status: Completed*
- **Upload Armor**: Enforced 50 MB file size limit, empty payload checks, `.pdf` extension whitelisting, and `%PDF` magic byte header validation.
- **Transaction & Tenant Isolation**: Implemented `_get_verified_document` preventing IDOR attacks across transaction bundles. Foreign document and risk finding queries strictly return HTTP 404.
- **Security Headers Middleware**: Implemented `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, and `Referrer-Policy: strict-origin-when-cross-origin`.
- **Health Probes**: Added `/api/v1/health/live` and `/api/v1/health/ready` verifying database, storage, and ML engine readiness.
- **Resilience Testing**: 8 new security/resilience tests added (90 backend tests total, 100% pass rate).

---

### Phase 12: Deployment & Portfolio Demo Experience
*Status: Completed*
- **Deterministic Golden Path Dataset**: Seeded transaction `skyview-a1204` with 4 full documents, area discrepancies, possession shifts, and asymmetric penalties.
- **Unified Launcher**: Created `scripts/run_clauseguard.sh` providing seamless one-command startup for both backend and frontend.
- **Portfolio Showcase Documentation**: Comprehensive `README.md` featuring full architectural overview, live demo script, test verification matrices, and academic highlights.
- **Production Build Verification**: Next.js production build passes with 11/11 static and dynamic routes compiled cleanly.
