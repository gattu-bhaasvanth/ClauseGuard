import { Transaction } from "@/types/transaction";
import {
  MOCK_ALL_TRANSACTIONS,
  MOCK_SKYVIEW_TRANSACTION,
} from "@/mock/demoData";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

/**
 * Fetch all transaction bundles from FastAPI backend,
 * falling back to local mock data if the backend is not reachable.
 */
export async function fetchTransactions(): Promise<any[]> {
  try {
    const res = await fetch(`${API_BASE}/transactions`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    return MOCK_ALL_TRANSACTIONS;
  }
}

/**
 * Fetch a single transaction bundle by ID from FastAPI backend,
 * falling back to the corresponding mock bundle if the backend is unreachable.
 */
export async function fetchTransactionById(id: string): Promise<any> {
  try {
    const res = await fetch(`${API_BASE}/transactions/${id}`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    if (id === "skyview-a1204") return MOCK_SKYVIEW_TRANSACTION;
    const found = MOCK_ALL_TRANSACTIONS.find((t) => t.id === id);
    return found || null;
  }
}

/**
 * Create a new property transaction workspace on the backend.
 */
export async function createTransaction(payload: {
  projectName: string;
  unit: string;
  developer: string;
  city: string;
  propertyType?: string;
  approxPrice?: number;
  carpetAreaSqFt?: number;
  superAreaSqFt?: number;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/transactions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to create transaction (${res.status})`);
  }
  return await res.json();
}

/**
 * Upload a transaction document to the backend pipeline.
 */
export async function uploadTransactionDocument(
  bundleId: string,
  file: File,
  documentType: string = "OTHER"
): Promise<any> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("document_type", documentType);
  formData.append("auto_extract_clauses", "true");

  const res = await fetch(`${API_BASE}/transactions/${bundleId}/documents/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to upload document (${res.status})`);
  }
  return await res.json();
}

/**
 * Register document metadata directly when raw PDF bytes are simulated or client-managed.
 */
export async function registerTransactionDocument(
  bundleId: string,
  payload: {
    file_name: string;
    document_type: string;
    file_size?: string;
    page_count?: number;
  }
): Promise<any> {
  const res = await fetch(`${API_BASE}/transactions/${bundleId}/documents`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to register document (${res.status})`);
  }
  return await res.json();
}

/**
 * Trigger cross-document consistency verification across an entire transaction bundle.
 */
export async function analyzeTransaction(bundleId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/transactions/${bundleId}/analyze`, {
    method: "POST",
    headers: { Accept: "application/json" },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to analyze transaction (${res.status})`);
  }
  return await res.json();
}

/**
 * Check backend health status.
 */
export async function checkBackendHealth(): Promise<{
  online: boolean;
  data?: any;
}> {
  try {
    const res = await fetch(`${API_BASE}/health`, {
      cache: "no-store",
    });
    if (!res.ok) return { online: false };
    const data = await res.json();
    return { online: true, data };
  } catch {
    return { online: false };
  }
}

/**
 * Ask a natural-language question against transaction documents via Phase 8 RAG endpoint.
 */
export async function queryTransactionRAG(
  bundleId: string,
  query: string,
  topK: number = 5
): Promise<any> {
  try {
    const res = await fetch(`${API_BASE}/transactions/${bundleId}/rag/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ query, topK }),
      cache: "no-store",
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error (${res.status})`);
    }
    return await res.json();
  } catch (err: any) {
    // If backend is unreachable, fallback to deterministic mock RAG response ONLY for demo transaction
    if (bundleId === "skyview-a1204") {
      const qLower = query.toLowerCase();
      if (qLower.includes("delay") || qLower.includes("handover") || qLower.includes("possession")) {
        return {
          query,
          answer:
            "According to **Clause 8.2: Possession Handover & Delay Penalty** of **Builder_Buyer_Agreement_SkyView_A1204.pdf** (Page 15):\n\n> \"8.2. In the event of delay in offering possession of the Apartment beyond the agreed date and grace period of 180 days, the Promoter shall pay compensation at the rate of Rs. 5/- (Rupees Five only) per sq. ft. of super area per month for the period of delay.\"\n\n**Key Terms Stated:** 180 days, Rs. 5/sq.ft/month.",
          grounded: true,
          status: "GROUNDED",
          confidence: 0.82,
          citations: [
            {
              documentId: "doc-bba-01",
              documentName: "Builder_Buyer_Agreement_SkyView_A1204.pdf",
              documentType: "BUILDER_BUYER_AGREEMENT",
              pageNumber: 15,
              clauseNumber: "Clause 8.2",
              clauseTitle: "Possession Handover & Delay Penalty",
              excerpt:
                "In the event of delay in offering possession of the Apartment beyond the agreed date and grace period of 180 days, the Promoter shall pay compensation at the rate of Rs. 5/- per sq. ft. of super area per month for the period of delay.",
              relevanceScore: 0.824,
            },
          ],
          bundleId,
          disclaimer: "ClauseGuard is an informational verification platform and does not provide legal advice.",
        };
      } else if (qLower.includes("interest") || qLower.includes("payment") || qLower.includes("installment")) {
        return {
          query,
          answer:
            "According to **Clause 5.3: Payment Default & Interest Rate** of **Builder_Buyer_Agreement_SkyView_A1204.pdf** (Page 13):\n\n> \"5.3. Time is of the essence. If the Allottee fails to pay any installment on or before the due date, the Allottee shall be liable to pay interest on delayed payment at the rate of 18% per annum compounded monthly from the due date until realization.\"\n\n**Key Terms Stated:** 18% per annum compounded monthly.",
          grounded: true,
          status: "GROUNDED",
          confidence: 0.83,
          citations: [
            {
              documentId: "doc-bba-01",
              documentName: "Builder_Buyer_Agreement_SkyView_A1204.pdf",
              documentType: "BUILDER_BUYER_AGREEMENT",
              pageNumber: 13,
              clauseNumber: "Clause 5.3",
              clauseTitle: "Payment Default & Interest Rate",
              excerpt:
                "If the Allottee fails to pay any installment on or before the due date, the Allottee shall be liable to pay interest on delayed payment at the rate of 18% per annum compounded monthly from the due date until realization.",
              relevanceScore: 0.831,
            },
          ],
          bundleId,
          disclaimer: "ClauseGuard is an informational verification platform and does not provide legal advice.",
        };
      } else if (qLower.includes("carpet") || qLower.includes("area") || qLower.includes("variation")) {
        return {
          query,
          answer:
            "According to **Clause 4.1: Measurement & Carpet Area Adjustments** of **Builder_Buyer_Agreement_SkyView_A1204.pdf** (Page 12):\n\n> \"4.1. The Allottee agrees that the Apartment has a RERA Carpet Area of 1,380 sq. ft. (128.20 sq. m.). The Promoter reserves the right to make architectural adjustments resulting in up to ±3% variation in carpet area without alteration to the agreed Total Consideration.\"\n\n**Key Terms Stated:** 1,380 sq. ft, ±3% allowable variation.",
          grounded: true,
          status: "GROUNDED",
          confidence: 0.84,
          citations: [
            {
              documentId: "doc-bba-01",
              documentName: "Builder_Buyer_Agreement_SkyView_A1204.pdf",
              documentType: "BUILDER_BUYER_AGREEMENT",
              pageNumber: 12,
              clauseNumber: "Clause 4.1",
              clauseTitle: "Measurement & Carpet Area Adjustments",
              excerpt:
                "The Allottee agrees that the Apartment has a RERA Carpet Area of 1,380 sq. ft. (128.20 sq. m.). The Promoter reserves the right to make architectural adjustments resulting in up to ±3% variation in carpet area without alteration to the agreed Total Consideration.",
              relevanceScore: 0.842,
            },
          ],
          bundleId,
          disclaimer: "ClauseGuard is an informational verification platform and does not provide legal advice.",
        };
      }
    }

    return {
      query,
      answer: `Based on the uploaded documents in this transaction bundle, there is no verified mention or specific provision regarding '${query}'. Please verify directly with the developer or request the relevant schedule/agreement.`,
      grounded: false,
      status: "INSUFFICIENT_EVIDENCE",
      confidence: 0.0,
      citations: [],
      bundleId,
      disclaimer: "ClauseGuard is an informational verification platform and does not provide legal advice.",
    };
  }
}

/**
 * Fetch all indexed chunks for a transaction bundle.
 */
export async function fetchTransactionChunks(bundleId: string): Promise<any[]> {
  try {
    const res = await fetch(`${API_BASE}/transactions/${bundleId}/rag/chunks`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    return [];
  }
}

/**
 * Fetch Phase 9 ML Intelligence Engine Status and baseline telemetry.
 */
export async function fetchEngineStatus(): Promise<any> {
  try {
    const res = await fetch(`${API_BASE}/intelligence/engine-status`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    return {
      active_engine: "HYBRID_ML_PROTOTYPE",
      model_name: "ClauseGuard Semantic Manifold Prototype Classifier",
      model_version: "v1.0.0",
      dataset_version: "cg-statutory-corpus-v1.0",
      fallback_available: true,
      benchmark_latency_ms: 0.03,
      baseline_macro_f1: 0.572,
      current_macro_f1: 0.8788,
      improvement_delta_f1: 0.3068,
      num_categories: 11,
      categories: [
        "Possession & Handover",
        "Payment Milestones & Delay Interest",
        "Carpet Area & Measurement Adjustments",
        "Cancellation & Earnest Money Forfeiture",
        "Alteration of Layout & Specifications",
        "Defects Liability & Structural Rectification",
        "Force Majeure & Uncontrollable Delays",
        "Dispute Resolution & Jurisdiction",
        "RERA & Statutory Approvals",
        "Maintenance & Additional Levies",
        "General Terms & Covenants",
      ],
    };
  }
}

/**
 * Fetch Phase 9 multi-model comparative bake-off evaluation metrics.
 */
export async function fetchBenchmarks(): Promise<any> {
  try {
    const res = await fetch(`${API_BASE}/intelligence/benchmarks`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    return null;
  }
}

/**
 * Classify arbitrary clause text using the live hybrid intelligence engine.
 */
export async function classifyClausePreview(title: string, text: string): Promise<any> {
  try {
    const res = await fetch(`${API_BASE}/intelligence/classify`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ title, text }),
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    return {
      primary_category: "General Terms & Covenants",
      confidence: 0.75,
      classification_source: "DETERMINISTIC_HEURISTIC",
      top_alternatives: [],
      explanation_notes: "Evaluated using local fallback mode.",
      risk_analysis: {
        status: "VERIFIED",
        analysis_summary: "Standard contractual provision categorized under General Terms.",
      },
    };
  }
}

/**
 * Phase 10: Fetch Transaction Command Center synthesized health and risk metrics.
 */
export async function fetchCommandCenter(bundleId: string): Promise<any> {
  try {
    const res = await fetch(`${API_BASE}/transactions/${bundleId}/copilot/command-center`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    if (bundleId === "skyview-a1204") {
      const { MOCK_COMMAND_CENTER_DATA } = await import("@/mock/demoData");
      return MOCK_COMMAND_CENTER_DATA;
    }
    throw err;
  }
}

/**
 * Phase 10: Ask a natural-language transaction question to the AI Copilot.
 */
export async function queryCopilot(
  bundleId: string,
  query: string,
  topK: number = 5
): Promise<any> {
  try {
    const res = await fetch(`${API_BASE}/transactions/${bundleId}/copilot/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ query, topK }),
      cache: "no-store",
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error (${res.status})`);
    }
    return await res.json();
  } catch (err: any) {
    if (bundleId === "skyview-a1204") {
      const qLower = query.toLowerCase();
      if (qLower.includes("delay") || qLower.includes("handover") || qLower.includes("possession")) {
        return {
          query,
          answer:
            "**Delayed Handover Provisions & Penalty Disparity Analysis:**\n\n• **Developer's Obligation (Clause 8.2)**: If handover extends past 31 December 2027 and the 180-day grace period (30 June 2028), the promoter pays compensation at ₹5 per sq.ft of super area per month (~₹11,000/mo = ~2.4% p.a.).\n• **Buyer's Obligation (Clause 4.3)**: Any delayed buyer installment incurs interest at **18% per annum compounded monthly** (~₹85,000/mo).\n• **Net Financial Impact**: There is a **₹74,000/month asymmetric penalty disparity** favoring the developer under RERA Section 18.",
          grounded: true,
          refused: false,
          intent: "DELAY_PENALTIES",
          confidence: 0.98,
          citations: [
            {
              documentId: "doc-bba-01",
              documentName: "Builder_Buyer_Agreement_SkyView_A1204.pdf",
              documentType: "BUILDER_BUYER_AGREEMENT",
              pageNumber: 15,
              clauseNumber: "Clause 8.2",
              clauseTitle: "Compensation for Delay in Possession",
              excerpt: "In the event of delay in offering possession of the Apartment, the Promoter shall pay compensation at the rate of Rs. 5/- per sq. ft. of super area per month for the period of delay beyond the grace period.",
              relevanceScore: 0.99,
            },
          ],
          bundleId,
          suggestedNextQuestions: [
            "What amendment should I ask the builder to make for delay penalties?",
            "Are there conflicting dates between the brochure and contract?",
          ],
          disclaimer: "ClauseGuard is an informational verification platform and does not provide legal advice.",
        };
      }
    }
    return {
      query,
      answer:
        "ClauseGuard could not find evidence in the uploaded transaction documents to answer this question. To prevent hallucinations, Copilot only answers based on verified document excerpts in this transaction bundle.",
      grounded: false,
      refused: true,
      intent: "GENERAL_GROUNDED",
      confidence: 0.0,
      citations: [],
      bundleId,
      suggestedNextQuestions: [
        "What are my biggest risks in this transaction?",
        "What clauses should I negotiate before signing?",
      ],
      disclaimer: "ClauseGuard is an informational verification platform and does not provide legal advice.",
    };
  }
}

/**
 * Phase 10: Fetch Explainable Risk Intelligence ("Why is this risky?") for a specific finding.
 */
export async function fetchExplainableRisk(
  bundleId: string,
  findingId: string
): Promise<any> {
  try {
    const res = await fetch(
      `${API_BASE}/transactions/${bundleId}/copilot/explain-risk/${findingId}`,
      { headers: { Accept: "application/json" }, cache: "no-store" }
    );
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    if (bundleId === "skyview-a1204") {
      return {
        findingId,
        title: "Asymmetrical Delay Penalties",
        severity: "CRITICAL",
        category: "PENALTY",
        plainEnglishHarm:
          "The agreement imposes an onerous 18% compound annual interest penalty on the purchaser for delayed payments, while limiting promoter liability for handover delay to a token ₹5 per sq.ft/month (~2.4% p.a.). This creates an asymmetric financial penalty disparity of approx ₹74,000 per month.",
        statutoryBenchmark:
          "Section 18 of RERA Act, 2016 and Pioneer Urban Land & Infrastructure v. Govindan Raghavan (2019) hold that one-sided penalty terms constitute an unfair trade practice, and allottees are entitled to interest at the statutory SBI MCLR + 2% rate.",
        quantifiedImpact: "₹74,000 / month penalty disparity between buyer default and developer delay.",
        lineage: {
          documentName: "Builder_Buyer_Agreement_SkyView_A1204.pdf",
          pageNumber: 15,
          clauseNumber: "Clause 8.2",
          clauseTitle: "Compensation for Delay in Possession",
          findingId,
          verbatimExcerpt: "In the event of delay in offering possession of the Apartment, the Promoter shall pay compensation at the rate of Rs. 5/- per sq. ft. of super area per month for the period of delay beyond the grace period.",
        },
        primaryEvidence: {
          documentName: "Builder_Buyer_Agreement_SkyView_A1204.pdf",
          pageNumber: 15,
          clauseNumber: "Clause 8.2",
          excerpt: "Promoter shall pay compensation at the rate of Rs. 5/- per sq. ft. of super area per month...",
        },
        recommendedNegotiationScript:
          "Clause 8.2 (Developer Delay Compensation) must be amended to provide for interest payable to the Allottee at SBI Highest MCLR + 2% per annum for every month of delay, on par with Clause 4.3.",
      };
    }
    throw err;
  }
}

/**
 * Phase 10: Fetch reconciled chronological timeline and obligations.
 */
export async function fetchTimeline(bundleId: string): Promise<any> {
  try {
    const res = await fetch(`${API_BASE}/transactions/${bundleId}/copilot/timeline`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    if (bundleId === "skyview-a1204") {
      const { MOCK_TIMELINE_DATA } = await import("@/mock/demoData");
      return MOCK_TIMELINE_DATA;
    }
    throw err;
  }
}

/**
 * Phase 10: Fetch structured Executive Transaction Brief.
 */
export async function fetchTransactionBrief(bundleId: string): Promise<any> {
  try {
    const res = await fetch(`${API_BASE}/transactions/${bundleId}/copilot/brief`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    if (bundleId === "skyview-a1204") {
      return {
        briefId: `brief-${bundleId}`,
        bundleId,
        generatedAt: new Date().toISOString(),
        project: "SkyView Residency",
        unit: "Flat A-1204",
        developer: "Skyline Urban Developers Pvt. Ltd.",
        healthScore: 74,
        riskLevel: "HIGH",
        totalFinancialExposure: "₹33.14 Lakhs",
        sections: [
          {
            sectionNumber: 1,
            sectionKey: "PROPERTY_SNAPSHOT",
            title: "Transaction & Property Snapshot",
            summary: "Acquisition of Flat A-1204 in SkyView Residency for ₹1.43 Cr.",
            bulletPoints: ["Unit: Flat A-1204 (Floor 12)", "Carpet Area: 1,380 sq.ft"],
            evidenceLineage: [{ document: "Builder_Buyer_Agreement_SkyView_A1204.pdf", excerpt: "Flat A-1204" }],
          },
        ],
        disclaimer: "ClauseGuard Transaction Brief is an automated forensic intelligence synthesis.",
      };
    }
    throw err;
  }
}

/**
 * Phase 10: Download vector-quality PDF of the Executive Transaction Brief.
 */
export async function downloadTransactionBriefPdf(bundleId: string): Promise<Blob> {
  const res = await fetch(`${API_BASE}/transactions/${bundleId}/copilot/brief/pdf`, {
    headers: { Accept: "application/pdf" },
  });
  if (!res.ok) throw new Error(`Failed to download brief PDF (${res.status})`);
  return await res.blob();
}

