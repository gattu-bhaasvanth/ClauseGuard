# ClauseGuard: Project Master Plan

This document outlines the end-to-end multi-phase execution strategy for **ClauseGuard** — an AI-Powered Real-Estate Transaction Intelligence Platform with Cross-Document Discrepancy Detection.

---

## Guiding Principles & Engineering Standards

1. **Cross-Document Discrepancy First**: Individual document summaries are secondary; the primary engineering focus is identifying contradictions, omissions, and mismatched obligations across multiple transaction documents.
2. **Strict Informational Boundaries**: The system is an informational tool, not a licensed legal practitioner. Every finding must use calibrated terminology (*"Potential inconsistency detected"*, *"Potential risk"*, *"Requires manual verification"*) and never offer definitive legal advice.
3. **Traceability to Raw Evidence**: Every flag, metric, or identified discrepancy must be traceable through an unbroken audit chain: `Document -> Page -> Clause -> Source Excerpt`.
4. **Honest ML Strategy**: No synthetic or pre-trained models will be claimed as "custom trained" until Phase 9, where a real domain-specific dataset is curated, annotated, trained, and benchmarked.
5. **Modular Architecture**: Clear separation of concerns between UI presentation, document ingestion/OCR, clause parsing, metadata normalization, cross-document comparison, and vector retrieval.

---

## Roadmap Overview

```
Phase 0: Project Foundation (Repository, Documentation & Environment)
  │
Phase 1: Frontend Application Shell & Document Viewer
  │
Phase 2: Backend Architecture, Database & Core API Foundation
  │
Phase 3: Robust Document Ingestion & OCR Processing Pipeline
  │
Phase 4: Clause Intelligence Engine (Segmentation & Taxonomy)
  │
Phase 5: Transaction Entity & Metadata Extraction Engine
  │
Phase 6: Cross-Document Intelligence & Inconsistency Detector
  │
Phase 7: Transaction Risk Analysis & Audit Report Engine
  │
Phase 8: Grounded Transaction RAG & Semantic Exploration
  │
Phase 9: Real Machine Learning Dataset Curation & Model Training
  │
Phase 10: Comprehensive Testing, Synthetic Stress-Testing & Benchmarks
  │
Phase 11: Production Hardening, Containerization & Deployment
```

---

## Detailed Phase Breakdown

---

### Phase 0: Project Foundation
*Status: In Progress*

- **Objective**: Establish a clean, professional, and reproducible repository foundation, directory structure, environment templates, and comprehensive architectural documentation.
- **Key Deliverables**:
  - Root directory scaffold (`frontend/`, `backend/`, `docs/`, `data/`, `tests/`, `scripts/`).
  - Standardized `.gitignore` covering Python, Node.js, environment secrets, and binary caches.
  - `.env.example` documenting all configuration keys without exposing secrets.
  - Git repository initialization and baseline commit.
  - `README.md`, `PROJECT_PLAN.md`, and `docs/ARCHITECTURE.md`.
- **Exit Criteria**: Clean repository verified, git tracked, documentation approved by user, zero bloat/unnecessary dependencies.

---

### Phase 1: Frontend Application Shell & Document Viewer
*Status: Planned*

- **Objective**: Construct a modern, intuitive Next.js frontend capable of managing transaction bundles and displaying synchronized PDF documents.
- **Key Deliverables**:
  - Next.js (App Router) + TypeScript + Tailwind CSS initial setup.
  - UI component design system leveraging `shadcn/ui` and `lucide-react`.
  - Transaction Project Dashboard: Create transaction bundles, upload multiple documents, view document statuses.
  - Split-screen Document Viewer powered by `PDF.js`:
    - Synchronized document viewing.
    - Page navigation, zoom, and search.
    - Bounding-box highlight overlay for extracted clauses and flagged text.
  - Inconsistency Alert Drawer: Displays findings and auto-scrolls the PDF viewer to the relevant page/clause.
- **Exit Criteria**: Responsive UI shell working with mock data, PDF viewer rendering sample documents and accepting coordinate-based highlights.

---

### Phase 2: Backend Architecture, Database & Core API Foundation
*Status: Planned*

- **Objective**: Establish the FastAPI backend service, asynchronous database connections, relational data models, and RESTful routing.
- **Key Deliverables**:
  - FastAPI application setup with modular routers (`/projects`, `/documents`, `/analysis`, `/rag`).
  - PostgreSQL database connection with async engine (`asyncpg` / `SQLAlchemy 2.0`).
  - Relational Database Models:
    - `TransactionBundle`: Represents a real-estate purchase transaction (e.g., "Apartment 402 - Green Valley").
    - `Document`: Represents individual files within a bundle (Brochure, Allotment Letter, BBA, Payment Schedule).
    - `DocumentPage`: Tracks text, dimensions, and OCR state per page.
    - `Clause`: Segmented clauses with type, risk category, and exact text boundaries.
    - `Finding`: Cross-document inconsistencies or clause-level risk flags.
  - Alembic database migration setup.
  - Pydantic v2 schemas for request validation and serializable response envelopes.
- **Exit Criteria**: FastAPI running with healthy `/health` endpoint, database migrations running cleanly, CRUD APIs functional for bundles and documents.

---

### Phase 3: Document Ingestion & OCR Processing Pipeline
*Status: Planned*

- **Objective**: Reliably extract structured text, layout coordinates, and page metadata from native digital PDFs, scanned documents, and stamped legal paper.
- **Key Deliverables**:
  - Fast digital extraction using PyMuPDF (`fitz`) and `pdfplumber` to retain character bounding boxes and line structures.
  - Heuristic text-density checker to automatically detect scanned or image-only pages.
  - OCR Fallback Pipeline using `PaddleOCR` (or Tesseract as an optional fallback) for scanned stamped papers.
  - Document normalization service: standardizing characters, cleaning header/footer noise, and preserving table layouts (crucial for payment schedules and area breakdowns).
  - Background asynchronous task pipeline for file processing to avoid blocking API threads.
- **Exit Criteria**: Pipeline extracts clean, structured text with page numbers and coordinate bounding boxes for both clean digital PDFs and scanned legal deeds.

---

### Phase 4: Clause Intelligence Engine
*Status: Planned*

- **Objective**: Parse raw document text into distinct, logically bounded legal clauses, classify clause types, and detect standard vs. non-standard provisions.
- **Key Deliverables**:
  - Clause Boundary Detection: Regex and layout-informed segmentation identifying numbered articles, headings, and sub-clauses.
  - Real-Estate Clause Taxonomy:
    - *Possession & Handover Terms*
    - *Defects Liability Period*
    - *Payment Milestones & Delay Interest*
    - *Earnest Money Forfeiture & Cancellation*
    - *Super Area vs. Carpet Area Definitions*
    - *Force Majeure & Extension Clauses*
    - *Dispute Resolution & Jurisdiction*
    - *Statutory Approvals & Compliance*
  - Clause Classification Service: Initial rule-based + zero-shot transformer classification mapping clauses into the taxonomy.
  - Obligation Extractor: Categorizing clause obligations into Buyer Obligations, Developer Obligations, and Mutual Rights.
- **Exit Criteria**: Raw document parsed into individual numbered clauses tagged with clause type and confidence scores.

---

### Phase 5: Transaction Entity & Metadata Extraction
*Status: Planned*

- **Objective**: Extract structured quantitative and qualitative transaction parameters from documents to populate the Unified Transaction Model.
- **Key Deliverables**:
  - Attribute Extraction Pipelines targeting:
    - **Property Metrics**: Carpet Area (sq. ft / sq. m), Built-Up Area, Super Built-Up Area, Undivided Share of Land (UDS), Unit/Apartment Number, Floor, Tower/Block.
    - **Financials**: Base Sale Price, Total Consideration, Booking Amount, PLC (Preferential Location Charges), Maintenance Deposits, Taxes/GST breakdown.
    - **Timelines**: Promised Possession Date, Grace Period duration, Defect Liability duration.
    - **Parties**: Buyer name(s), Developer legal entity, Co-signers, Project Registered Name.
    - **Payment Schedule**: Individual milestones (e.g., "On completion of 4th slab: 10%"), due dates, and amounts.
  - Value Normalization: Standardizing units (sq. ft vs sq. m), currencies, and date formats (ISO 8601) to make cross-comparison deterministic.
- **Exit Criteria**: Normalized JSON representation of transaction metadata extracted accurately from brochures, allotment letters, and agreements.

---

### Phase 6: Cross-Document Intelligence & Inconsistency Detector
*Status: Planned*

- **Objective**: Implement the core differentiator of ClauseGuard — automated cross-document consistency verification across an entire transaction bundle.
- **Key Deliverables**:
  - **Transaction Knowledge Graph / Alignment Matrix**: Aligning extracted entities across the bundle's documents.
  - **Deterministic Discrepancy Evaluators**:
    - *Area Discrepancy Rule*: Compare carpet area claimed in brochure vs. allotment letter vs. sale agreement.
    - *Pricing & Milestone Discrepancy Rule*: Compare total price in allotment letter vs. sum of payment schedule installments vs. agreement consideration.
    - *Timeline Discrepancy Rule*: Compare advertised delivery date in marketing materials vs. contractual delivery date and grace periods in agreement.
    - *Party Discrepancy Rule*: Detect differences in developer legal entities or missing co-allottees.
  - **Evidence Pairing Service**: Constructing paired evidence payloads:
    - `Primary Document`: Excerpt, Page, Clause
    - `Contradicting Document`: Excerpt, Page, Clause
    - `Discrepancy Category`: Area / Price / Possession / Obligation
    - `Severity`: Informational / Moderate / Critical
- **Exit Criteria**: Demonstrable automated detection of planted inconsistencies between a brochure and agreement with exact citations for both documents.

---

### Phase 7: Risk Analysis & Audit Report Engine
*Status: Planned*

- **Objective**: Evaluate asymmetric risk, identify unfavorable clauses, and generate an evidence-backed informational Transaction Audit Report.
- **Key Deliverables**:
  - Asymmetric Risk Detector:
    - Penalties for delayed payment (e.g., Buyer pays 18% p.a.) vs. penalties for delayed possession (e.g., Builder pays ₹5/sq.ft/month ~ 2-3% p.a.).
    - Unilateral rights to alter layout, specifications, or building plans without buyer consent.
    - Aggressive forfeiture of earnest money on minor defaults.
  - Risk Scoring & Summarization: Compute risk indices per category without providing legal counsel.
  - Informational Transaction Audit Report:
    - Executive Summary of Transaction Bundle
    - Discrepancy Table with deep links to PDF pages
    - High-Risk Clause Breakdown
    - Missing Documents Checklist (e.g., "No Sanction Plan or Allotment Letter attached")
    - Export to PDF and JSON formats.
- **Exit Criteria**: Generated report displaying clear, evidence-linked findings with the required informational disclaimers.

---

### Phase 8: Grounded Transaction RAG & Semantic Exploration
*Status: Planned*

- **Objective**: Enable natural-language query capabilities over the entire transaction bundle with strictly grounded citations and zero hallucinations.
- **Key Deliverables**:
  - Document chunking strategy preserving clause hierarchy and document provenance.
  - Vector indexing using `sentence-transformers` and ChromaDB / FAISS.
  - Hybrid Search: Combining dense semantic embeddings with BM25 lexical keyword matching (crucial for exact clause numbers, dates, and amounts).
  - Contextual Prompt Engineering with Modular LLM layer (Gemini, Claude, GPT, or local models).
  - Citation Guardrail: Answers must strictly reference `[Doc: Agreement, Page: 14, Clause: 9.2]` and refuse to speculate beyond the uploaded documents.
- **Exit Criteria**: Q&A interface successfully answers user questions (e.g., "What happens if I delay a payment by 15 days?") citing the exact agreement clause.

---

### Phase 9: Real Machine Learning Dataset Curation & Model Training
*Status: Planned*

- **Objective**: Curate a dedicated, high-quality real-estate contract dataset and train fine-tuned models for specialized clause extraction and classification tasks.
- **Key Deliverables**:
  - Dataset Definition & Annotation Guidelines: Standardizing labels across real-estate transaction agreements.
  - Dataset Curation: Anonymized contracts + synthetically generated realistic variation sets.
  - Fine-Tuning:
    - Clause Classification Model (Hugging Face Transformers / RoBERTa / DeBERTa).
    - Named Entity Recognition (NER) for real-estate financial & property attributes.
  - Model Evaluation: Precision, Recall, F1-scores, and confusion matrices against holdout test splits.
  - Model Export & Inference Integration (ONNX runtime or Hugging Face pipeline).
- **Exit Criteria**: Published training metrics, test set evaluation reports, and production-ready inference service replacing heuristic parsers.

---

### Phase 10: Comprehensive Testing, Synthetic Stress-Testing & Benchmarks
*Status: Planned*

- **Objective**: Verify end-to-end reliability, numerical precision, OCR resilience, and security across the entire platform.
- **Key Deliverables**:
  - Automated Unit Tests: Backend routes, database operations, Pydantic schemas.
  - Synthetic Evaluation Benchmark: A benchmark suite of 25+ paired document bundles containing known, controlled discrepancies (area, price, possession, penalties).
  - Automated Discrepancy Recall & Precision Metric: Measuring percentage of planted inconsistencies successfully detected.
  - Security & PII Assessment: Redaction of sensitive personal information (buyer Aadhaar/PAN, banking credentials) during processing.
- **Exit Criteria**: >90% test coverage on core discrepancy engines, automated test suite passing in CI.

---

### Phase 11: Production Hardening, Containerization & Deployment
*Status: Planned*

- **Objective**: Package the application into reproducible containers, establish automated CI/CD pipelines, and prepare for production deployment.
- **Key Deliverables**:
  - Dockerfiles for frontend (Node multi-stage build) and backend (Python 3.11 slim).
  - `docker-compose.yml` orchestrating Next.js, FastAPI, PostgreSQL, and vector storage.
  - GitHub Actions CI/CD workflows for linting, type-checking, and test execution.
  - Production environment configuration guides and secret management protocols.
- **Exit Criteria**: One-command local startup via Docker Compose, automated CI pipeline passing.
