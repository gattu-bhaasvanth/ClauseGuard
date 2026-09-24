# Phase 10 — Transaction Intelligence Copilot Walkthrough & Golden Path Demonstration

## 1. Executive Overview

**Phase 10** transforms ClauseGuard from individual forensic document analyzers into a unified, executive-grade **Transaction Intelligence Copilot**.

Operating 100% locally on CPU without external cloud AI dependencies, Phase 10 synthesizes:
- **Phase 4**: Deterministic Statutory Benchmark Rules
- **Phase 5**: Entity, Property & Financial Metadata Extraction
- **Phase 6**: Cross-Document Discrepancy & Lineage Engine
- **Phase 7**: Risk Analysis & Audit Report Engine
- **Phase 8**: Grounded FastEmbed Semantic Retrieval & Chunk Embeddings
- **Phase 9**: Domain-Specific Hybrid ML Classification & Calibration

---

## 2. The 8-Step Golden Path Demonstration (`skyview-a1204`)

This walkthrough verifies the end-to-end functionality on the flagship **SkyView Residency — Flat A-1204** transaction bundle.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   Phase 10 Golden Path Verification Sequence                           │
│                                                                                        │
│  [Step 1] Command Center Cockpit ──► [Step 2] Asymmetric Penalty Inspection            │
│                 │                                      │                               │
│                 ▼                                      ▼                               │
│  [Step 3] RERA Sec 18 Quantified Harm ◄─── [Step 4] Ask Copilot (Cmd+K)                │
│                 │                                      │                               │
│                 ▼                                      ▼                               │
│  [Step 5] Grounded Citation Verification ──► [Step 6] Reconciled Timeline Track        │
│                 │                                      │                               │
│                 ▼                                      ▼                               │
│  [Step 7] Evidence Lineage Graph ─────────► [Step 8] Executive Brief & PDF Export      │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Step 1: Open the Transaction Command Center
- **Action**: Navigate to `/dashboard/transactions/skyview-a1204`.
- **Expected Verification**:
  - The **Command Center** tab renders automatically as the default workspace.
  - Overall Transaction Health Index displays **74/100** (`HIGH` risk alert).
  - Financial Exposure Hero displays **Total Capital At Risk: ₹33.14 Lakhs**.
  - All 5 Multi-Dimensional Risk Vectors render with vector health gauges:
    1. *Financial Exposure Risk* (Score: 40, CRITICAL)
    2. *Contractual Asymmetry Risk* (Score: 35, CRITICAL)
    3. *Timeline & Delivery Risk* (Score: 50, HIGH)
    4. *Dimensional Variance Risk* (Score: 50, HIGH)
    5. *Document Completeness Risk* (Score: 60, MEDIUM)
  - 5 Priority Action Items are listed with severity pills, document citations, and actionable recommendations for buyer counsel.

### Step 2: Inspect Asymmetrical Delay Penalty
- **Action**: Click on the **Contractual Asymmetry Risk** vector or click **Inspect** on Priority Action Item #2.
- **Expected Verification**:
  - The `ExplainableRiskDrawer` opens from the right side of the screen.
  - The drawer displays finding `risk-01`: **Asymmetrical Delay Penalties** with a `CRITICAL` severity badge.

### Step 3: Review Quantified Legal Explanations
- **Action**: Inspect the contents of the `ExplainableRiskDrawer`.
- **Expected Verification**:
  - **Plain-English Harm Analysis**: Explains that late buyer payments incur 18% p.a. interest, whereas developer delay is limited to token ₹5/sq.ft/month (~2.4% p.a.).
  - **Quantified Financial Impact Card**: Displays **₹74,000 / month penalty disparity** between buyer default charge and developer compensation.
  - **Statutory Regulatory Benchmark**: Cites **RERA Section 18** (SBI Highest MCLR + 2%) and Supreme Court precedent (*Pioneer Urban Land & Infrastructure v. Govindan Raghavan*).
  - **5-Tier Evidence Lineage**:
    - Document: `Builder_Buyer_Agreement_SkyView_A1204.pdf`
    - Page: `Page 15`
    - Clause: `Clause 8.2`
    - Finding ID: `risk-01`
    - Verbatim Operative Excerpt: *"In the event of delay in offering possession of the Apartment, the Promoter shall pay compensation at the rate of Rs. 5/- per sq. ft. of super area per month for the period of delay beyond the grace period."*
  - **Negotiation Amendment Script**: Ready-to-copy draft clause amending developer compensation to SBI MCLR + 2% per annum.
  - Pressing `Escape` cleanly closes the drawer.

### Step 4: Engage the AI Transaction Copilot (`Cmd+K`)
- **Action**: Press `Cmd+K` (or `Ctrl+K` on Windows/Linux) or click the **Ask Copilot** header button.
- **Expected Verification**:
  - The `TransactionCopilotPanel` opens with keyboard focus automatically in the text input.
  - Type or click the suggested question chip:
    `"What happens if the builder delays handover beyond December 2027?"`
  - Press `Enter` or click `Ask`.

### Step 5: Verify Grounded Multi-Document Evidence
- **Action**: Inspect Copilot's response.
- **Expected Verification**:
  - Intent is recognized as `DELAY_PENALTIES`.
  - The assistant outputs a structured analysis detailing:
    - Developer's obligation under Clause 8.2 (₹9,100/mo on 1,820 sq.ft super area = ~2.4% p.a.).
    - Buyer's late charge under Clause 4.3 (18% p.a. compounded monthly = ~₹85,000/mo).
    - ₹74,000/month asymmetric disparity.
    - Grounding badge: **Grounded in Evidence** with emerald styling.
    - Citation chip: `Clause 8.2 • Builder_Buyer_Agreement_SkyView_A1204.pdf` linking to Page 15.
  - Suggested follow-up prompt chips appear below the message.

#### Anti-Hallucination Invariant Check
- **Action**: Enter an ungrounded or speculative query:
  `"What is the developer's CEO personal home address and stock price?"`
- **Expected Verification**:
  - Copilot triggers the strict anti-hallucination refusal contract:
    `"ClauseGuard could not find evidence in the uploaded transaction documents to answer this question. To prevent hallucinations, Copilot only answers based on verified document excerpts in this transaction bundle."`
  - Zero fabricated facts, zero hallucinated dates, status: `refused: true`.

### Step 6: Explore Reconciled Timeline & Obligation Intelligence
- **Action**: Switch to the **Timeline & Obligations** tab.
- **Expected Verification**:
  - Reconciled chronological track displays 7 milestones.
  - **Timeline Conflict Alert** prominently flags:
    - Advertised Brochure Handover Date: **31 Dec 2026** (`MARKETING`).
    - Allotment Letter Target Handover: **30 June 2027** (`MARKETING`).
    - Agreement Binding Deadline: **31 Dec 2027** (`CONTRACTUAL`).
    - Unconditional Grace Buffer Limit: **30 June 2028** (`INFERRED`).
    - Structural Milestone Calls: 4th Floor Slab (`UNCERTAIN`, linked to ₹14.25 Lakhs installment).
  - Certainty filter pills allow isolating `CONTRACTUAL`, `CONFLICTS`, and `UNCERTAIN` milestones.

### Step 7: Trace Evidence Lineage Graph
- **Action**: Switch to the **Evidence Lineage Graph** tab.
- **Expected Verification**:
  - Visual lineage displays the unbroken forensic chain:
    $$\text{Transaction: SkyView A-1204} \longrightarrow \text{Document: BBA.pdf} \longrightarrow \text{Page 15} \longrightarrow \text{Clause 8.2} \longrightarrow \text{Risk Finding: risk-01} \longrightarrow \text{Verbatim Excerpt}$$
  - Toggle between **Asymmetrical Delay Penalty Lineage** and **Carpet Area Discrepancy Lineage**.

### Step 8: Generate Executive Transaction Brief & Export PDF
- **Action**: Click the **Executive Brief** button in the header or Command Center.
- **Expected Verification**:
  - The `TransactionBriefModal` opens displaying all 7 structured sections:
    1. *Transaction & Property Snapshot*
    2. *Executive Assessment & Health Rating* (74/100)
    3. *Financial Exposure Matrix* (₹33.14 Lakhs capital at risk)
    4. *Critical Contractual Milestones & Timeline*
    5. *Key Discrepancies & Advertising Divergence* (70 sq.ft shortfall & 12-month delivery slippage)
    6. *High-Priority Asymmetric Clauses*
    7. *Recommended Buyer Action Plan & Amendment Draft*
  - Every section includes underlying evidence citations.
  - Click **Export PDF**:
    - Generates and streams vector-quality PDF `ClauseGuard_Brief_skyview-a1204.pdf` rendered via PyMuPDF (`fitz`).
    - Download executes smoothly in the browser.

---

## 3. Verification Gates Summary

| Gate | Description | Command | Result |
|---|---|---|---|
| **Gate 1** | Pre-Phase-10 Regression Baseline | `pytest tests/backend` & `npm test` | **64 Backend + 15 Frontend tests passed** |
| **Gate 2** | Orchestration & Knowledge Graph | `pytest tests/backend/test_transaction_intelligence.py` | **3 tests passed** |
| **Gate 3** | Copilot Grounding & Anti-Hallucination | `pytest tests/backend/test_copilot.py` | **6 tests passed** |
| **Gate 4** | Timeline 5 Certainty States | `pytest tests/backend/test_timeline_intelligence.py` | **1 test passed** |
| **Gate 5** | 7-Section Brief & PDF Export | `pytest tests/backend/test_transaction_brief.py` | **1 test passed** |
| **Gate 6** | Copilot API Endpoints | `pytest tests/backend/test_copilot_api.py` | **7 tests passed** |
| **Gate 7** | Frontend UI & Accessibility | `node --test tests/copilot_ui.test.mjs` | **8 tests passed (23 total)** |
| **Gate 8** | Production Build | `npm run build` | **Compiled successfully (0 errors)** |
| **Gate 9** | Full Backend Regression Suite | `pytest tests/backend` | **82 passed in 2.23s** |
| **Gate 10** | Golden Path Demonstration | Walkthrough on `skyview-a1204` | **Verified 100%** |
