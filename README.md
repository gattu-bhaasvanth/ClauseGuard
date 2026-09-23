# ClauseGuard

> **AI-Powered Real-Estate Transaction Intelligence Platform**  
> *Cross-document verification, risk analysis, and discrepancy detection for property transactions.*

---

## 🏛️ Vision & Purpose

Real estate transactions are among the largest and most complex financial commitments individuals and institutions undertake. Typically, a buyer or investor receives a scattered bundle of documents across months:
- Marketing Brochures & Spec Sheets
- Booking Applications & Allotment Letters
- Builder-Buyer Agreements (BBA) / Agreements for Sale
- Payment Schedules & Demand Notes
- Encumbrance Certificates, Sanction Plans, and NOCs

In today's market, analyzing these documents manually is exhausting, error-prone, and perilous. Furthermore, existing AI legal tech tools typically treat documents in isolation—offering generic single-document summaries ("PDF → Summary") that miss the critical gaps between what was promised and what was contractually stipulated.

**ClauseGuard is NOT a simple single-PDF summarizer.**

**ClauseGuard's core differentiator is Cross-Document Transaction Intelligence.** It ingests the entire transaction bundle, builds a unified transaction model, and performs automated cross-document consistency checks:
- **Carpet Area vs. Super Built-up Area**: Detects if a brochure promised 1,450 sq. ft. while the formal sale agreement specifies 1,380 sq. ft.
- **Possession Timelines & Grace Periods**: Pinpoints discrepancies between marketing representations and binding contractual grace periods or force majeure exemptions.
- **Financial & Payment Milestones**: Validates whether the milestone installment amounts on payment schedules match the total consideration stated in the allotment letter and agreement.
- **Asymmetric Liabilities**: Flags unfair penalty clauses (e.g., buyer pays 18% p.a. for delayed installment, while builder pays a nominal rate or gets extended grace periods).

---

## ⚖️ Important Product Positioning & Legal Disclaimer

> **IMPORTANT NOTICE: INFORMATIONAL DOCUMENT-ANALYSIS SYSTEM ONLY**  
> ClauseGuard is an automated document analysis and consistency verification system designed to assist buyers, advisors, and professionals in reviewing transaction paperwork.
> 
> - **ClauseGuard is NOT a law firm, attorney, or licensed legal practitioner.**
> - **ClauseGuard does NOT provide legal advice, legal opinions, or binding guarantees.**
> - All outputs are classified as informational flags such as **"Potential inconsistency detected"**, **"Potential risk"**, or **"Requires manual verification"**.
> - Every finding is anchored directly to its origin: **Document → Page → Clause → Exact Excerpt/Evidence**.

---

## 🚀 Key Planned Capabilities

1. **Multi-Document Bundle Ingestion**
   - Seamlessly group related transaction documents into a unified "Transaction File".
   - Support for vector PDFs, scanned contracts, mobile uploads, and image-based agreements with OCR fallback.

2. **Cross-Document Discrepancy Engine**
   - Correlate structured attributes across documents (Area, Price, Possession Date, Parties, Milestones).
   - Side-by-side evidence comparison showing the exact differing excerpts and page numbers.

3. **Clause Extraction & Risk Engine**
   - Identify critical clauses: indemnity, forfeiture of earnest money, unilateral variation rights, possession handover delays, dispute resolution jurisdiction.
   - Categorize clauses into balanced, standard, and high-risk terms.

4. **Interactive Document & Clause Viewer**
   - Split-screen workspace: document preview (PDF.js) with real-time text highlighting synchronized with AI findings.
   - Deep-link directly from an inconsistency alert to the source text on Page X of Document A and Page Y of Document B.

5. **Retrieval-Augmented Transaction Q&A (RAG)**
   - Ask complex natural language questions grounded strictly across all uploaded transaction documents.
   - Answers cite specific pages, clauses, and documents with zero hallucinations.

---

## 🛠️ Planned Technology Stack

### Frontend
- **Framework**: Next.js (App Router, React 19 / TypeScript)
- **Styling**: Tailwind CSS, PostCSS
- **Component Library**: shadcn/ui (Radix UI primitives)
- **Animations & Transitions**: Framer Motion
- **Document Viewing**: PDF.js / react-pdf with bounding-box highlight overlays
- **Icons**: Lucide React

### Backend
- **Framework**: Python 3.11+ / FastAPI
- **Data Validation & Schemas**: Pydantic v2
- **Server**: Uvicorn / Gunicorn
- **Task Execution**: Async background worker / background tasks

### Database & Storage
- **Primary Database**: PostgreSQL (relational schema for projects, transactions, documents, clauses, findings)
- **Object Storage**: Local filesystem in development; S3 / GCS-compatible storage in production
- **Vector Database**: ChromaDB / FAISS for semantic chunk search and cross-clause retrieval

### Document Extraction & OCR
- **Digital PDF Extraction**: PyMuPDF (`fitz`), `pdfplumber`
- **OCR Fallback**: PaddleOCR (for scanned agreements and stamped paper)

### AI, NLP & Machine Learning
- **Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2` / `bge-base`)
- **NLP**: Hugging Face Transformers
- **LLM Provider Layer**: Modular abstraction supporting Google Gemini, OpenAI, Anthropic, and local models.
- **Custom ML**: Proprietary dataset creation and custom classification/NER models scheduled for Phase 9 (no false claims of pre-trained custom ML models).

---

## 🗺️ High-Level Project Roadmap

| Phase | Title | Focus Area | Status |
| :--- | :--- | :--- | :--- |
| **Phase 0** | **Foundation** | Workspace structure, documentation, environment template, Git init | **In Progress** |
| **Phase 1** | **Frontend Core** | Next.js setup, Tailwind, shadcn/ui, transaction dashboard, PDF viewer shell | *Planned* |
| **Phase 2** | **Backend & DB** | FastAPI foundation, PostgreSQL schema, Alembic migrations, REST API routes | *Planned* |
| **Phase 3** | **Document Processing** | PyMuPDF text pipeline, page segmentation, PaddleOCR fallback | *Planned* |
| **Phase 4** | **Clause Intelligence** | Clause boundary detection, classification, obligation identification | *Planned* |
| **Phase 5** | **Transaction Metadata** | Structured entity extraction (Area, Price, Dates, Parties) | *Planned* |
| **Phase 6** | **Cross-Document Engine** | Discrepancy detector, multi-document alignment matrix | *Planned* |
| **Phase 7** | **Risk Engine** | Risk taxonomy, asymmetrical clause detector, informational report generator | *Planned* |
| **Phase 8** | **RAG & Search** | Vector indexation, grounded bundle Q&A, citation synthesis | *Planned* |
| **Phase 9** | **Real ML Development** | Dataset annotation, model training, evaluation & metrics | *Planned* |
| **Phase 10** | **Testing & Hardening** | Unit & integration tests, synthetic stress tests, security review | *Planned* |
| **Phase 11** | **Deployment** | Docker containers, CI/CD pipeline, production launch | *Planned* |

For comprehensive details on each phase, see [PROJECT_PLAN.md](file:///Users/gattubhaasvanth/Desktop/ClauseGuard/PROJECT_PLAN.md).

---

## 📂 Repository Layout

```
ClauseGuard/
├── frontend/             # Next.js web application
├── backend/              # FastAPI backend API services
├── docs/                 # Architectural specifications, API schemas, and guides
│   └── ARCHITECTURE.md   # High-level system architecture and data flows
├── data/                 # Data directory (uploads, samples, processed text)
│   ├── samples/          # Synthetic & anonymized sample transaction documents
│   ├── uploads/          # Local uploaded files (gitignored)
│   ├── processed/        # Extracted text and clause chunks (gitignored)
│   └── embeddings/       # Local vector store indices (gitignored)
├── tests/                # Automated test suites
│   ├── frontend/         # Component and UI integration tests
│   └── backend/          # API, extractor, and rule engine unit tests
├── scripts/              # Development and evaluation utility scripts
├── .gitignore            # Comprehensive ignores for Node, Python, and environments
├── .env.example          # Environment variable template (no secrets)
├── README.md             # Project overview and roadmap
└── PROJECT_PLAN.md       # Comprehensive multi-phase execution plan
```

---

## 🏁 Phase 0 Verification

Phase 0 sets up the foundational repository scaffolding, documentation, and configuration templates without installing heavy dependencies.

To verify Phase 0 locally:
```bash
# 1. Verify directory structure
ls -la

# 2. Verify git status
git status

# 3. Verify environment template
cat .env.example
```
