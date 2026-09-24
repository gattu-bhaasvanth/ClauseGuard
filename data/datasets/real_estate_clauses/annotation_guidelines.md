# ClauseGuard Real-Estate Clause Annotation & Provenance Guidelines
Version: 1.0 (Phase 9 Specification)

---

## 1. Objective and Provenance Standards

ClauseGuard requires an auditable, domain-specific dataset of Indian and common-law real-estate agreement clauses. To comply with ethical ML, copyright, and legal data governance principles:
1. **Public Domain / Open Statutory Sources Only**: Training data must originate from officially published statutory model agreements (e.g. Central RERA Form 'A', state-notified model agreements, published gazette regulations, and public judicial records).
2. **Mandatory Provenance Metadata**: Every annotated example must retain unbroken provenance:
   - `clause_id`: Unique identifier (e.g., `IN-RERA-CENTRAL-FORM-A-CL01`)
   - `title`: Clause heading as drafted
   - `text`: Verbatim clause text
   - `category`: Exactly one of the 11 canonical taxonomy categories
   - `source_document`: Official title of the parent document
   - `source_url`: Verifiable public URL / gazette archive reference
   - `jurisdiction`: ISO 3166-2 sub-division code (e.g., `IN-DL`, `IN-MH`, `IN-KA`, `IN-HR`, `IN-TN`, or `IN-FED`)
   - `source_type`: Category of source (`Statutory Model Agreement`, `State Gazette Notification`, `Appellate Court Disclosure`, `Public Sector Conveyance`)
   - `license`: Open access license (`Government Open Data / Public Domain`, `CC-BY-4.0`, or `Public Legal Document`)
   - `date`: Date of publication or statutory notification (ISO 8601 `YYYY-MM-DD`)
   - `annotation_version`: Schema version (e.g., `v1.0-verified`)
   - `annotator_id`: Identifying tag of the curator or legal reviewer
   - `entities`: Array of token-level NER spans (start_char, end_char, label, text)
3. **Strict Synthetic PII Masking**: Real-world personal identity identifiers (individual citizen names, personal phone numbers, PAN cards, Aadhaar IDs, bank account numbers, specific private home addresses) must be scrubbed or replaced with generic placeholders (`[BUYER_NAME]`, `[CO_BUYER]`, `[PROMOTER_LLP]`, `[UNIT_NO]`).

---

## 2. Canonical 11-Category Taxonomy Definitions

### Category 1: Possession & Handover (`Possession & Handover`)
- **Canonical Identifier**: `POSSESSION_TERMS`
- **Definition**: Provisions governing the agreed date of physical completion, handover of possession, occupancy/completion certificate requirements, notice of offer of possession, fit-out periods, and builder delay compensation terms.
- **Inclusions**:
  - Scheduled completion date covenants.
  - Grace period / permissible delay buffer terms granted to developer.
  - Procedure for notice of possession, joint inspection, and snag list.
  - Compensation or interest payable by the promoter for delayed handover.
  - Conveyance deed execution and transfer of title.
- **Exclusions**:
  - Pure payment installments tied to completion milestones (belong in `Payment Milestones & Delay Interest`).
  - Acts of God excuses for delay without specific possession terms (belong in `Force Majeure & Uncontrollable Delays`).

### Category 2: Payment Milestones & Delay Interest (`Payment Milestones & Delay Interest`)
- **Canonical Identifier**: `PAYMENT_TERMS`
- **Definition**: Terms stipulating total consideration breakdown, payment milestones, due dates, advance booking amounts, and buyer interest penalties for late installment payments.
- **Inclusions**:
  - Total purchase consideration and taxes breakdown (GST, stamp duty).
  - Construction-linked installment schedules (e.g., foundation, plinth, casting of slabs).
  - Delay payment interest rates levied on allottee (e.g., SBI MCLR + 2%, 18% p.a.).
  - "Time is of the essence" covenants concerning buyer payments.
- **Exclusions**:
  - Earnest money forfeiture rules upon cancellation (belong in `Cancellation & Earnest Money Forfeiture`).
  - Common area maintenance charges (belong in `Maintenance & Additional Levies`).

### Category 3: Carpet Area & Measurement Adjustments (`Carpet Area & Measurement Adjustments`)
- **Canonical Identifier**: `AREA_SPECIFICATIONS`
- **Definition**: Definitions of net usable carpet area, built-up area, super area, undivided share of land (UDS), and stipulations regarding acceptable measurement variations and corresponding financial adjustments.
- **Inclusions**:
  - Explicit RERA carpet area measurements (sq.ft / sq.m).
  - Tolerances for permissible area variation (e.g. up to ±3% or 5%).
  - Financial adjustments or refunds if final measured area deviates from agreed area.
  - Undivided proportionate share in land (UDS) covenants.
- **Exclusions**:
  - Unilateral alteration of layout plans without area variation (belong in `Alteration of Layout & Specifications`).

### Category 4: Cancellation & Earnest Money Forfeiture (`Cancellation & Earnest Money Forfeiture`)
- **Canonical Identifier**: `CANCELLATION_FORFEITURE`
- **Definition**: Stipulations regarding termination of agreement, buyer withdrawal rights, developer default termination, earnest money deduction percentages, and refund timelines.
- **Inclusions**:
  - Grounds on which developer may cancel the allotment or agreement.
  - Forfeiture percentage of earnest money / booking amount (e.g., 10%, 20%).
  - Buyer rights to terminate upon promoter delay and receive full refund with interest.
  - Timelines for return of balance funds to allottee upon cancellation.
- **Exclusions**:
  - Default interest rate without cancellation (belong in `Payment Milestones & Delay Interest`).

### Category 5: Alteration of Layout & Specifications (`Alteration of Layout & Specifications`)
- **Canonical Identifier**: `ALTERATION_VARIATION`
- **Definition**: Provisions reserving or restricting rights to alter building architectural plans, structural designs, unit layouts, common fixtures, or brand specifications.
- **Inclusions**:
  - Developer clauses claiming discretion to effect modifications due to architectural necessity.
  - Statutory consent clauses requiring two-thirds allottee consent for major layout revisions.
  - Replacement of agreed material finishes or sanitary fittings with equivalent grades.
- **Exclusions**:
  - Area changes resulting purely from re-measurement without structural plan alteration (belong in `Carpet Area & Measurement Adjustments`).

### Category 6: Defects Liability & Structural Rectification (`Defects Liability & Structural Rectification`)
- **Canonical Identifier**: `DEFECTS_LIABILITY`
- **Definition**: Warranties against structural defects, poor workmanship, defective materials, and promoter obligations to rectify defects within the statutory warranty period.
- **Inclusions**:
  - Statutory 5-year defect liability covenants under RERA Section 14(3).
  - Procedure for notifying developer of structural cracks, seepage, or plumbing defects.
  - Rectification timeline (e.g., 30 days from notice) without additional cost to allottee.
  - Exclusions from warranty (wear and tear, unauthorized tenant modifications).
- **Exclusions**:
  - Routine maintenance operations after handover to resident association (belong in `Maintenance & Additional Levies`).

### Category 7: Force Majeure & Uncontrollable Delays (`Force Majeure & Uncontrollable Delays`)
- **Canonical Identifier**: `FORCE_MAJEURE`
- **Definition**: Clauses defining unexpected external events beyond promoter control that legally excuse delivery delays and suspend contractual performance obligations.
- **Inclusions**:
  - Enumeration of force majeure triggers: flood, earthquake, war, strike, pandemic, government embargo, civil unrest.
  - Suspension of interest and liability during force majeure subsistence.
  - Obligation to notify allottee within specified days of occurrence.
- **Exclusions**:
  - Developer-caused financial shortage, contractor disputes, or market slump (standard statutory law excludes commercial hardship from force majeure).

### Category 8: Dispute Resolution & Jurisdiction (`Dispute Resolution & Jurisdiction`)
- **Canonical Identifier**: `DISPUTE_JURISDICTION`
- **Definition**: Mechanisms for resolving legal disputes between parties, including arbitration, mediation, choice of law, and territorial jurisdiction of courts.
- **Inclusions**:
  - Arbitration agreements: seat, venue, rules (Arbitration and Conciliation Act, 1996).
  - Appointment procedure for sole arbitrator or tribunal.
  - Territorial jurisdiction clauses (e.g., "Courts at Mumbai alone shall have jurisdiction").
  - Mutual conciliation or settlement conferences prior to formal litigation.
- **Exclusions**:
  - Statutory RERA grievance rights (when focused on RERA complaint authority, evaluate under `RERA & Statutory Approvals` unless structured as court jurisdiction).

### Category 9: RERA & Statutory Approvals (`RERA & Statutory Approvals`)
- **Canonical Identifier**: `STATUTORY_COMPLIANCE`
- **Definition**: Covenants, representations, and warranties concerning statutory project registration, building sanctions, environmental NOCs, and statutory title compliance.
- **Inclusions**:
  - Promoter representation of valid RERA registration number and quarterly project updates.
  - Confirmation of sanctioned layout plan, commencement certificate, and building bye-laws compliance.
  - Fire safety NOC, airport height NOC, and environmental impact clearance citations.
  - Title flow representations and encumbrance disclosures.
- **Exclusions**:
  - Defect liability statutory periods (belong in `Defects Liability & Structural Rectification`).

### Category 10: Maintenance & Additional Levies (`Maintenance & Additional Levies`)
- **Canonical Identifier**: `MAINTENANCE_CHARGES`
- **Definition**: Provisions detailing recurring maintenance fees, sinking funds, society formation charges, ad-hoc external development charges (EDC/IDC), and common amenity upkeep.
- **Inclusions**:
  - Monthly/annual per-square-foot common maintenance rates.
  - Advance maintenance deposits (e.g. 1–2 years advance) and sinking fund contributions.
  - Handover of maintenance management to Allottee Association / Resident Welfare Association (RWA).
  - Electricity substation installation charges, meter connection fees, and club subscription.
- **Exclusions**:
  - Total purchase consideration installments (belong in `Payment Milestones & Delay Interest`).

### Category 11: General Terms & Covenants (`General Terms & Covenants`)
- **Canonical Identifier**: `GENERAL_TERMS`
- **Definition**: Standard contract boilerplate, legal definitions, notices, severability, entire agreement clauses, and miscellaneous covenants.
- **Inclusions**:
  - Method and address for serving legal notices.
  - Severability of invalid or illegal terms.
  - Entire agreement / integration clause superseding prior representations or brochures.
  - Binding effect on successors, legal heirs, and permitted assigns.
- **Exclusions**:
  - Clauses containing substantive subject-matter matching Categories 1–10.

---

## 3. Real-Estate NER / Entity Annotation Schema

The following 8 entities are annotated using exact character start and end offsets:
1. `CARPET_AREA`: Exact numerical carpet area with unit (e.g., `"1,020 sq.ft"`).
2. `SUPER_AREA`: Exact numerical super built-up area with unit (e.g., `"1,450 sq.ft"`).
3. `TOTAL_PRICE`: Agreed purchase price / total consideration (e.g., `"Rs. 1,45,00,000/-"`).
4. `BOOKING_AMOUNT`: Advance booking or earnest money (e.g., `"Rs. 10,00,000/-"`).
5. `POSSESSION_DATE`: Promised delivery date (e.g., `"31st December 2026"`).
6. `GRACE_PERIOD`: Permitted delay extension period (e.g., `"6 (six) months"`).
7. `DELAY_RATE`: Explicit late payment or delayed handover interest rate (e.g., `"18% per annum"`).
8. `RERA_ID`: State registration alphanumeric string (e.g., `"P51800012345"`).

---

## 4. Contamination Prevention and Data Partitioning

1. **Document Grouped Splitting**: All clauses originating from a single source deed or model agreement must be placed in the *same* partition split (`train`, `val`, or `test`). Cross-split contamination of clauses from the same document is strictly prohibited.
2. **De-duplication**: Text normalization and hashing are executed during splitting. Any exact hash collision causes the preparation script to abort with an error.
3. **8-Gram Jaccard Threshold**: Maximum allowable 8-gram Jaccard similarity between any clause in `test.jsonl` and `train.jsonl` is **0.40**.
