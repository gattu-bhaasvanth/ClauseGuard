# ClauseGuard

> **AI-Powered Real-Estate Transaction Intelligence Platform**  
> *Cross-document verification, asymmetric risk analysis, grounded copilot, and discrepancy detection for property transactions.*

[![Backend Tests](https://img.shields.io/badge/Backend%20Tests-90%2F90%20Passing-emerald?style=for-the-badge&logo=pytest)](file:///Users/gattubhaasvanth/Desktop/ClauseGuard/tests/backend)
[![Frontend Tests](https://img.shields.io/badge/Frontend%20Tests-23%2F23%20Passing-emerald?style=for-the-badge&logo=node.js)](file:///Users/gattubhaasvanth/Desktop/ClauseGuard/frontend/tests)
[![Architecture](https://img.shields.io/badge/Phases%200--12-100%25%20Delivered-blue?style=for-the-badge)](file:///Users/gattubhaasvanth/Desktop/ClauseGuard/PROJECT_PLAN.md)
[![Zero External AI API](https://img.shields.io/badge/Inference-100%25%20Local%20CPU-purple?style=for-the-badge)](file:///Users/gattubhaasvanth/Desktop/ClauseGuard/backend/app/intelligence/ml)
[![License](https://img.shields.io/badge/License-MIT-gray?style=for-the-badge)](file:///Users/gattubhaasvanth/Desktop/ClauseGuard/LICENSE)

---

## 🏛️ Executive Summary & Real-World Problem

Real estate transactions represent the largest single financial commitment most individuals and corporate buyers ever make. In practice, a transaction never consists of a single document. Instead, buyers receive a fragmented bundle of paperwork spread across months:
1. **Marketing Brochures & Floor Plans** (Initial promises, advertised carpet area, amenities)
2. **Booking Forms & Allotment Letters** (Unit reservation, initial payment, projected handover date)
3. **Builder-Buyer Agreements (BBA) / Agreements for Sale** (30–60 page dense legal contracts)
4. **Milestone Payment Schedules** (Installment schedules tied to construction phases)
5. **Sanction Letters, NOCs & Encumbrance Certificates**

### Why Existing Legal-Tech Fails
Mainstream legal tech tools and generic AI chat assistants treat documents as **isolated silos** (*"Upload PDF → Summarize"*). This single-document paradigm completely misses the most dangerous risks in real estate transactions:
- **Contractual Contradictions**: Marketing brochures promise 1,450 sq.ft carpet area, while Clause 4.1 of the fine-print agreement quietly defines carpet area as 1,380 sq.ft with a unilateral ±3% variation clause.
- **Hidden Delivery Postponements**: Allotment letters promise handover by June 2027, whereas the formal agreement specifies December 2027 plus an unconditional 180-day developer grace period.
- **Grossly Asymmetrical Liabilities**: Clause 5.3 penalizes late buyer installments at **18% p.a. compounded monthly**, while Clause 8.2 compensates delayed builder delivery at a nominal **₹5/sq.ft/month (~2.4% p.a.)**.

**ClauseGuard solves this by treating the entire transaction as a unified intelligence graph.** It correlates, cross-checks, and validates facts across every document in the bundle, highlighting inconsistencies and quantifying financial risk with mathematical precision.

---

## ⚖️ Important Product Positioning & Legal Notice

> **INFORMATIONAL TRANSACTION INTELLIGENCE TOOL ONLY**  
> ClauseGuard is an automated document analysis and cross-verification system designed to assist buyers, real-estate advisors, and legal professionals.
> 
> - **ClauseGuard is NOT a law firm and does NOT provide legal advice or legal opinions.**
> - Outputs are classified as informational verification findings: `Potential inconsistency detected`, `Potential risk`, or `Requires manual verification`.
> - Every metric, inconsistency, and risk finding is backed by an unbroken 5-tier audit trail:  
>   `Document → Page Number → Clause → Statutory Benchmark → Financial Exposure`.

---

## 🌟 Key Platform Capabilities

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           CLAUSEGUARD COMMAND CENTER                            │
├─────────────────────┬───────────────────────────┬───────────────────────────────┤
│ Transaction Health  │ Quantified Exposure       │ Critical Blockers             │
│       74 / 100      │   ₹25.65 Lakh Risk        │ 2 Inconsistencies, 4 Risks    │
└─────────────────────┴───────────────────────────┴───────────────────────────────┘
                                       │
     ┌─────────────────────────────────┼─────────────────────────────────┐
     ▼                                 ▼                                 ▼
┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐
│ Cross-Doc Discrepancy   │ │ Explainable Risk Engine │ │ Transaction Copilot     │
│ Carpet Area Mismatch    │ │ 5-Tier Audit Lineage    │ │ Evidence-Grounded Q&A   │
│ Timeline Postponement   │ │ Statutory RERA Recourse │ │ Cmd+K Keyboard Shortcut │
│ Milestone Sum Mismatch  │ │ Asymmetric Penalties    │ │ Strict Citation Guard   │
└─────────────────────────┘ └─────────────────────────┘ └─────────────────────────┘
                                       │
     ┌─────────────────────────────────┼─────────────────────────────────┐
     ▼                                 ▼                                 ▼
┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐
│ Intelligent Timeline    │ │ Split Document Viewer   │ │ ML Model Diagnostics    │
│ 5 Certainty States      │ │ Synchronized PDF.js     │ │ Real RERA Dataset       │
│ Contractual vs Inferred │ │ Real-time Bounding Box  │ │ Multi-Model Bake-off    │
│ Conflicting Date Alerts │ │ Deep-Linked Highlights  │ │ Zero-Cost Local Engine  │
└─────────────────────────┘ └─────────────────────────┘ └─────────────────────────┘
```

### 1. Transaction Command Center
- **Composite Transaction Health Score (0–100)**: Evaluates structural integrity, statutory compliance, and contractual balance.
- **Quantified Exposure Radar**: Aggregates calculated potential financial risks (e.g. ₹25.65L total exposure).
- **Executive Transaction Brief**: Generates a professional 7-section memorandum ready for one-click PDF export.

### 2. Cross-Document Inconsistency Detector
- Automatically pairs contradicting text across disparate files:
  - *Brochure Page 4* (1,450 sq.ft) vs. *BBA Page 12 Clause 4.1* (1,380 sq.ft) → **70 sq.ft loss (₹10.35 Lakh exposure)**.
  - *Allotment Letter Page 2* (June 2027) vs. *BBA Page 19 Clause 11.2* (Dec 2027 + 180-day grace) → **12-month delivery shift**.

### 3. Explainable Risk Intelligence & 5-Tier Lineage
- Unpacks complex legal traps into clear, actionable breakdowns.
- Evaluates contracts against statutory benchmarks (e.g., **RERA Section 18** reciprocal interest mandates).
- Every finding displays complete provenance: Document → Page → Clause → Statutory Benchmark → Exposure.

### 4. Grounded Transaction Copilot (Cmd+K)
- Interactive conversational assistant powered by strictly cited transaction facts.
- **Zero Hallucination Guarantee**: Every substantive claim includes interactive citation pills deep-linking to the exact source clause.
- **Explicit Refusal Contract**: Inquiries outside the transaction documents are safely declined (*"I cannot find evidence in the transaction documents..."*).

### 5. Intelligent Multi-State Timeline
- Classifies transaction dates into 5 distinct certainty states:
  - `CONTRACTUAL`: Enforceable contractual commitments.
  - `INFERRED`: Derived from statutory rules or milestone triggers.
  - `MARKETING`: Representations made in sales literature.
  - `CONFLICTING`: Mismatched dates across documents flagged for immediate clarification.
  - `UNCERTAIN`: Ambiguous or conditional date projections.

### 6. Domain-Specific ML Classifier & Model Diagnostics Hub
- 11-category real-estate legal taxonomy (Possession, Area, Payment, Forfeiture, Alteration, etc.).
- Evaluated on a holdout dataset of 60 real Indian RERA clauses across 6 official authorities (`corpus_manifest.json`).
- Hybrid architecture: Production ML Ridge classifier (F1: 0.933, latency: 1.1ms) with automatic deterministic fallback.
- Live interactive Model Diagnostics Hub in `/dashboard/settings` with multi-model bake-off metrics.

### 7. Production Hardening & Tenant Isolation
- **Upload Armor**: 50 MB file limit, `.pdf` whitelisting, and `%PDF` magic byte header verification.
- **IDOR Protection**: Strict cross-bundle document and finding isolation (`_get_verified_document`).
- **Security Headers**: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection`, strict referrer policy.
- **Orchestration Probes**: Production-grade `/api/v1/health/live` and `/api/v1/health/ready`.

---

## ⚡ Quickstart Guide

### Prerequisites
- **Python**: 3.9+ (Python 3.11+ recommended)
- **Node.js**: 18+ (Node 20 recommended)
- **Operating System**: macOS, Linux, or Windows (WSL2)

### Option A: One-Command Development Launcher (Recommended)
Clone the repository and run the unified startup script:
```bash
git clone https://github.com/your-username/ClauseGuard.git
cd ClauseGuard

# Grant execution permission and launch both services
chmod +x scripts/run_clauseguard.sh
./scripts/run_clauseguard.sh
```
This automatically starts:
- **FastAPI Backend**: `http://127.0.0.1:8000` (API Docs: `http://127.0.0.1:8000/docs`)
- **Next.js Web UI**: `http://localhost:3000`
- **Demo Bundle**: `http://localhost:3000/dashboard/transactions/skyview-a1204`

---

### Option B: Manual Step-by-Step Setup

#### 1. Backend Setup
```bash
cd backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

#### 2. Frontend Setup
```bash
cd frontend

# Install Node dependencies
npm install

# Build production bundle
npm run build

# Start Next.js production server
npm start -- -p 3000
```

---

## 🎬 Golden Path Demo Walkthrough (Evaluator Script)

Follow this 5-minute walkthrough to experience the complete capabilities of ClauseGuard:

| Step | Action | What to Observe |
| :--- | :--- | :--- |
| **1. Landing Page** | Visit `http://localhost:3000` | Note the dark-mode aesthetic, v1.0 badge, and value proposition. Click **"Launch Platform"**. |
| **2. Portfolio Dashboard** | Navigate to `/dashboard` | View active transaction bundles. Note the **SkyView Residency (Flat A-1204)** card showing Health Score **74/100** and 6 flagged issues. Click into the card. |
| **3. Command Center** | Overview Tab | Review the **Financial Exposure Radar** (₹25.65L), composite health breakdown, and critical blockers. |
| **4. Copilot in Action** | Press `Cmd+K` (or click **"Ask Copilot"**) | Copilot drawer slides out. Click the suggestion prompt: *"Explain the delay penalty discrepancy"*. Observe the answer citing **Clause 5.3 vs. Clause 8.2** with clickable citation pills. |
| **5. Hallucination Refusal** | Ask: *"What is the developer's stock price?"* | Observe the Copilot's refusal contract: correctly refuses to fabricate out-of-scope facts. |
| **6. Explainable Risk** | Click **"Explain Risk"** on *Asymmetrical Delay Penalties* | 5-tier lineage drawer displays: BBA → Page 15 → Clause 8.2 → RERA Sec 18 Benchmark → ₹5.40L financial impact. |
| **7. Cross-Doc Inconsistencies** | Click the **"Inconsistencies"** tab | Review the side-by-side comparison of **1,450 sq.ft** (Brochure) vs. **1,380 sq.ft** (BBA). |
| **8. Intelligent Timeline** | Click the **"Timeline"** tab | Notice color-coded certainty states: Contractual dates (emerald), Marketing dates (blue), and Conflicting dates (amber). |
| **9. Document Analysis Workspace** | Click **"Open Split Analysis"** | Full split-screen viewer opens (`/analysis`). Browse extracted clauses, observe ML Confidence Badges (e.g. 96%), and click **"Inspect Classification"**. |
| **10. Model Diagnostics** | Visit `/dashboard/settings` | Scroll to the **Local Model Diagnostics Hub**. View the 3-model bake-off table, Macro F1 metrics, and test live predictions in the interactive sandbox. |
| **11. Executive Brief** | Back on Overview, click **"Generate Brief"** | Full 7-section printable memorandum renders with financial exposure breakdown and export button. |

---

## 🧪 Verification & Test Suite

ClauseGuard is backed by a comprehensive automated test harness covering backend REST endpoints, extraction logic, ML bake-off benchmarks, security isolation, and frontend UI components.

### Run All Backend Tests (90 Tests)
```bash
./backend/.venv/bin/pytest tests/backend -v
```
```
============================== 90 passed in 2.33s ==============================
tests/backend/test_copilot.py ............ [PASSED]
tests/backend/test_cross_document.py ...... [PASSED]
tests/backend/test_hybrid_classifier.py .. [PASSED]
tests/backend/test_ingestion.py .......... [PASSED]
tests/backend/test_metadata_extraction.py  [PASSED]
tests/backend/test_rag.py ................ [PASSED]
tests/backend/test_security_resilience.py  [PASSED]
tests/backend/test_transaction_brief.py .. [PASSED]
tests/backend/test_transactions.py ....... [PASSED]
```

### Run All Frontend Integration Tests (23 Tests)
```bash
cd frontend && npm test
```
```
▶ Phase 10 Frontend Intelligence & Copilot UI Integration Tests (8 tests) [PASSED]
▶ Phase 9 Frontend Intelligence & ML UI Integration Tests (8 tests)      [PASSED]
▶ Phase 8 Frontend RAG UI Integration Tests (7 tests)                    [PASSED]
ℹ tests 23 | pass 23 | fail 0 | duration_ms 55ms
```

### Verify Production Frontend Build
```bash
cd frontend && npm run build
```
```
✓ Compiled successfully
✓ Generating static pages (11/11)
✓ Finalizing page optimization
```

---

## 📊 Machine Learning Model Architecture & Provenance

| Metric / Parameter | Value | Details |
| :--- | :--- | :--- |
| **Dataset Size** | 60 annotated clauses | Curated from 7 official Indian real-estate statutory documents |
| **Licensing** | Public Domain / Open Gov | MahaRERA, HRERA, UP RERA, Delhi High Court |
| **Provenance Manifest** | `corpus_manifest.json` | 100% source-tracked with URLs, gazette numbers, and hashes |
| **Selected Model** | TF-IDF + Ridge Classifier | Sublinear TF, 1-3 n-grams, Platt sigmoid probability calibration |
| **Test Macro F1** | **0.933** | Multi-candidate bake-off winner over FastEmbed & Prototype models |
| **Inference Latency** | **1.1 ms / clause** | Runs entirely in-process on CPU (zero GPU requirement) |
| **Fallback Guarantee** | Deterministic Heuristic | Automatic graceful fallback if ML confidence drops below 0.65 |

For comprehensive model architecture and evaluation graphs, see [docs/PHASE_9_MODEL_CARD.md](file:///Users/gattubhaasvanth/Desktop/ClauseGuard/docs/PHASE_9_MODEL_CARD.md).

---

## 📁 Repository Structure

```
ClauseGuard/
├── backend/                              # FastAPI Backend Application
│   ├── app/
│   │   ├── api/v1/                       # REST API route handlers
│   │   │   ├── copilot.py                # Copilot, Brief, and Timeline endpoints
│   │   │   ├── documents.py              # Ingestion, validation & clause routes
│   │   │   ├── health.py                 # Liveness & readiness probes
│   │   │   ├── rag.py                    # Vector search & citation retrieval
│   │   │   └── transactions.py           # Bundle management & health scoring
│   │   ├── intelligence/                 # Core analysis engines
│   │   │   ├── ml/                       # Local inference, bake-off & hybrid classifier
│   │   │   ├── inconsistency_detector.py # Cross-document discrepancy evaluators
│   │   │   ├── risk_engine.py            # Asymmetric penalty & clause risk analysis
│   │   │   └── taxonomy.py               # 11-category statutory legal taxonomy
│   │   ├── models/                       # SQLAlchemy 2.0 relational models
│   │   ├── schemas/                      # Pydantic v2 validation schemas
│   │   └── services/                     # Orchestration & demo data seeding
│   └── requirements.txt                  # Python dependencies
├── frontend/                             # Next.js 14 Frontend Application
│   ├── src/
│   │   ├── app/                          # App Router pages (Dashboard, Analysis, Settings)
│   │   ├── components/
│   │   │   ├── copilot/                  # Command Center, Copilot, Timeline, Brief
│   │   │   ├── documents/                # PDF.js split viewer & clause inspector
│   │   │   ├── ml/                       # Confidence badges & diagnostics hub
│   │   │   └── transactions/             # Inconsistency cards & risk radar
│   │   └── lib/api.ts                    # Typed API client with offline resilience
│   └── package.json                      # Node dependencies & test runner
├── data/
│   ├── datasets/real_estate_clauses/     # Indian RERA statutory dataset & manifest
│   ├── models/                           # Serialized bake-off & production models
│   └── clauseguard.db                    # Pre-seeded SQLite database
├── docs/                                 # Technical documentation & walkthroughs
│   ├── ARCHITECTURE.md                   # Full system architecture specification
│   ├── PHASE_9_MODEL_CARD.md             # ML dataset provenance & evaluation card
│   └── PHASE_10_WALKTHROUGH.md           # Copilot & Command Center walkthrough
├── scripts/
│   ├── run_clauseguard.sh                # One-command unified demo launcher
│   └── generate_sample_pdfs.py           # Synthetic PDF generation utility
├── tests/
│   ├── backend/                          # 90 pytest unit, integration & security tests
│   └── frontend/                         # 23 Node.js test runner suites
├── PROJECT_PLAN.md                       # Comprehensive 12-phase project master plan
└── README.md                             # Project portfolio overview
```

---

## 🛡️ Security & Privacy Architecture

- **Hermetic Local Operation**: Operates 100% locally with SQLite and local ONNX embeddings (`all-MiniLM-L6-v2-onnx`). Zero transaction data, personal information, or document excerpts are ever sent to external cloud APIs.
- **Upload Armor**: Enforces 50 MB payload caps, strictly whitelisted `.pdf` file extensions, empty byte detection, and `%PDF-` magic byte verification.
- **Multi-Tenant IDOR Isolation**: Cross-bundle queries are verified at the database layer; unauthorized document access strictly returns HTTP 404.
- **Hardened HTTP Headers**: Strict security headers injected on every API response (`nosniff`, `DENY`, XSS protection, strict referrer policy).

---

## 👥 Authors & Academic Attribution

Developed as a capstone portfolio and final-year engineering project in AI-Powered Legal & Financial Technology.

- **Developer**: Haasvanth Gattu
- **Domain Focus**: Real-Estate Transaction Intelligence, Cross-Document Consistency Verification, Local Explainable ML.
- **License**: MIT License. See [LICENSE](file:///Users/gattubhaasvanth/Desktop/ClauseGuard/LICENSE) for details.
