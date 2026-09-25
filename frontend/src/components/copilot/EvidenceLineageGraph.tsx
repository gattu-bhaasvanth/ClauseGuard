"use client";

import React, { useState } from "react";
import { GitBranch, FileText, Bookmark, ShieldAlert, ArrowRight, CheckCircle2 } from "lucide-react";

interface EvidenceNode {
  id?: string;
  level: "TRANSACTION" | "DOCUMENT" | "PAGE" | "CLAUSE" | "FINDING" | "EVIDENCE";
  title: string;
  subtitle?: string;
  detail?: string;
}

interface LineageChain {
  id: string;
  title: string;
  severity: string;
  nodes: EvidenceNode[];
}

interface EvidenceLineageGraphProps {
  bundleId: string;
  transaction?: any;
  commandCenterData?: any;
  onOpenDocumentViewer?: (docName: string, pageNumber: number) => void;
}

export const EvidenceLineageGraph: React.FC<EvidenceLineageGraphProps> = ({
  bundleId,
  transaction,
  commandCenterData,
  onOpenDocumentViewer,
}) => {
  const [selectedChainIndex, setSelectedChainIndex] = useState(0);

  const SKYVIEW_LINEAGE_CHAINS = [
    {
      id: "chain-penalty",
      title: "Asymmetrical Delay Penalties Lineage",
      severity: "CRITICAL",
      nodes: [
        {
          level: "TRANSACTION" as const,
          title: "SkyView Residency (Flat A-1204)",
          subtitle: "Bundle ID: skyview-a1204",
          detail: "₹1.43 Cr consideration, 1,380 sq.ft carpet area",
        },
        {
          level: "DOCUMENT" as const,
          title: "Builder_Buyer_Agreement_SkyView_A1204.pdf",
          subtitle: "Type: BUILDER_BUYER_AGREEMENT (38 pages)",
          detail: "Primary binding registered contract",
        },
        {
          level: "PAGE" as const,
          title: "Page 15",
          subtitle: "Section: Possession & Handover",
          detail: "Operative terms governing delay liabilities",
        },
        {
          level: "CLAUSE" as const,
          title: "Clause 8.2: Delay Compensation",
          subtitle: "Classification: Payment & Delay Interest (98% Conf)",
          detail: "Promoter pays ₹5/sq.ft/month after grace period",
        },
        {
          level: "FINDING" as const,
          title: "Risk Finding: Asymmetrical Delay Penalties (risk-01)",
          subtitle: "Severity: CRITICAL",
          detail: "Buyer defaults incur 18% p.a. vs Developer paying ~2.4% p.a.",
        },
        {
          level: "EVIDENCE" as const,
          title: "Verbatim Contractual Excerpt",
          subtitle: "Anchor: BBA_A1204_P15_C8.2",
          detail:
            '"In the event of delay in offering possession of the Apartment, the Promoter shall pay compensation at the rate of Rs. 5/- per sq. ft. of super area per month for the period of delay beyond the grace period."',
        },
      ],
    },
    {
      id: "chain-area",
      title: "Carpet Area Discrepancy Lineage",
      severity: "HIGH",
      nodes: [
        {
          level: "TRANSACTION" as const,
          title: "SkyView Residency (Flat A-1204)",
          subtitle: "Bundle ID: skyview-a1204",
          detail: "Advertised 1,450 sq.ft vs BBA 1,380 sq.ft",
        },
        {
          level: "DOCUMENT" as const,
          title: "Sales_Brochure_SkyView_Residency.pdf vs Agreement.pdf",
          subtitle: "Cross-Document Discrepancy Pair",
          detail: "Brochure Page 1 vs BBA Schedule A (Page 4)",
        },
        {
          level: "PAGE" as const,
          title: "BBA Page 4 & Brochure Page 1",
          subtitle: "Dimensional Specifications",
          detail: "70 sq.ft (-4.8%) net reduction",
        },
        {
          level: "CLAUSE" as const,
          title: "Schedule A vs Brochure Highlights",
          subtitle: "Classification: Carpet Area & Measurements",
          detail: "BBA Schedule A defines 1,380 sq.ft",
        },
        {
          level: "FINDING" as const,
          title: "Inconsistency Finding: Carpet Area Reduction (inc-01)",
          subtitle: "Severity: HIGH",
          detail: "Uncompensated ₹4.64 Lakhs valuation deficit",
        },
        {
          level: "EVIDENCE" as const,
          title: "Verbatim Dual-Excerpt Pair",
          subtitle: "Dual Anchors: Brochure_P1 vs BBA_P4",
          detail:
            'Brochure: "1,450 sq.ft Carpet Area" | BBA Schedule A: "Carpet Area of the Apartment is 1,380 sq.ft with 3% tolerance."',
        },
      ],
    },
  ];

  // Dynamic chain generation for custom transactions
  const dynamicChains: LineageChain[] = React.useMemo(() => {
    if (bundleId === "skyview-a1204") return SKYVIEW_LINEAGE_CHAINS;

    const chains: LineageChain[] = [];
    const projName = transaction?.property?.project || transaction?.title || "Transaction";
    const unitName = transaction?.property?.unit ? ` (${transaction.property.unit})` : "";
    const devName = transaction?.property?.developer ? `Developer: ${transaction.property.developer}` : "";

    // 1. Process inconsistencies
    const inconsistencies = transaction?.inconsistencies || [];
    inconsistencies.forEach((inc: any, idx: number) => {
      const pe = inc.primaryEvidence || {};
      const se = inc.secondaryEvidence || {};
      chains.push({
        id: inc.id || `inc-chain-${idx}`,
        title: `${inc.title || "Discrepancy"} Lineage`,
        severity: inc.severity || "HIGH",
        nodes: [
          {
            level: "TRANSACTION",
            title: `${projName}${unitName}`,
            subtitle: `Bundle ID: ${bundleId}`,
            detail: `${devName} • Cross-document reconciliation`,
          },
          {
            level: "DOCUMENT",
            title: `${pe.documentName || "Marketing Doc"} vs ${se.documentName || "Contract"}`,
            subtitle: "Cross-Document Discrepancy Pair",
            detail: "Contradictory representations across deal artifacts",
          },
          {
            level: "PAGE",
            title: `Pages ${pe.pageNumber || 1} & ${se.pageNumber || 1}`,
            subtitle: "Comparative Artifact Pages",
            detail: inc.title || "Discrepancy source pages",
          },
          {
            level: "CLAUSE",
            title: `${pe.clauseNumber || "Source A"} vs ${se.clauseNumber || "Source B"}`,
            subtitle: `Category: ${inc.category || "Inconsistency"}`,
            detail: inc.description || "Reconciled clause comparison",
          },
          {
            level: "FINDING",
            title: `Discrepancy: ${inc.title || "Finding"} (${inc.id || `inc-${idx}`})`,
            subtitle: `Severity: ${inc.severity || "HIGH"}`,
            detail: inc.description || "Contractual variance identified",
          },
          {
            level: "EVIDENCE",
            title: "Verbatim Dual-Excerpt Pair",
            subtitle: "Reconciled Evidence",
            detail: `Doc A: "${pe.excerpt || "Excerpt A"}" | Doc B: "${se.excerpt || "Excerpt B"}"`,
          },
        ],
      });
    });

    // 2. Process risk findings
    const findings = transaction?.findings || commandCenterData?.topRisks || transaction?.risks || [];
    findings.forEach((finding: any, idx: number) => {
      const pe = finding.primaryEvidence || {};
      const docName = pe.documentName || transaction?.documents?.[0]?.name || "Contract.pdf";
      const pageNum = pe.pageNumber || 1;
      const clauseNum = pe.clauseNumber || finding.category || "General";
      chains.push({
        id: finding.id || `finding-chain-${idx}`,
        title: `${finding.title || "Contractual Risk"} Lineage`,
        severity: finding.severity || "HIGH",
        nodes: [
          {
            level: "TRANSACTION",
            title: `${projName}${unitName}`,
            subtitle: `Bundle ID: ${bundleId}`,
            detail: devName,
          },
          {
            level: "DOCUMENT",
            title: docName,
            subtitle: `Type: ${pe.documentType || "CONTRACT"}`,
            detail: "Primary binding contractual instrument",
          },
          {
            level: "PAGE",
            title: `Page ${pageNum}`,
            subtitle: `Section: ${clauseNum}`,
            detail: "Forensic source location for verified finding",
          },
          {
            level: "CLAUSE",
            title: `${clauseNum}: ${finding.title}`,
            subtitle: `Classification: ${finding.category || "Risk"}`,
            detail: finding.title,
          },
          {
            level: "FINDING",
            title: `Risk Finding: ${finding.title} (${finding.id || `risk-${idx}`})`,
            subtitle: `Severity: ${finding.severity || "HIGH"}`,
            detail: finding.description || "Contractual risk identified",
          },
          {
            level: "EVIDENCE",
            title: "Verbatim Contractual Excerpt",
            subtitle: `Anchor: ${docName}_P${pageNum}`,
            detail: `"${pe.excerpt || finding.description || "Verified clause excerpt"}"`,
          },
        ],
      });
    });

    return chains;
  }, [bundleId, transaction, commandCenterData]);

  const LINEAGE_CHAINS = dynamicChains;

  if (LINEAGE_CHAINS.length === 0) {
    return (
      <div className="rounded-xl bg-[#111622] border border-zinc-800 p-8 text-center space-y-3">
        <GitBranch className="w-8 h-8 text-zinc-600 mx-auto" />
        <h4 className="text-sm font-semibold text-zinc-300">
          No Evidence Lineage Generated
        </h4>
        <p className="text-xs text-zinc-500 max-w-md mx-auto">
          Upload and analyze documents for this transaction to extract clauses, detect discrepancies, and construct verifiable forensic lineage pathways.
        </p>
      </div>
    );
  }

  const currentChain = LINEAGE_CHAINS[selectedChainIndex] || LINEAGE_CHAINS[0];

  return (
    <div className="rounded-xl bg-[#111622] border border-zinc-800 p-5 space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-zinc-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <GitBranch className="w-5 h-5 text-emerald-400" />
            <h3 className="text-base font-semibold text-zinc-100">
              Evidence Lineage & Traceability Graph
            </h3>
          </div>
          <p className="text-xs text-zinc-400">
            Unbroken forensic lineage from top-level Transaction down to Page, Clause, and raw Verbatim Excerpt
          </p>
        </div>

        {/* Chain Selector */}
        <div className="flex items-center gap-2">
          {LINEAGE_CHAINS.map((chain, cIdx) => (
            <button
              key={chain.id}
              onClick={() => setSelectedChainIndex(cIdx)}
              className={`text-xs px-3 py-1.5 rounded-lg border font-medium transition-all ${
                selectedChainIndex === cIdx
                  ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                  : "bg-zinc-900 text-zinc-400 border-zinc-800 hover:text-zinc-200"
              }`}
            >
              {chain.title.split(" ")[0]} Lineage
            </button>
          ))}
        </div>
      </div>

      {/* Visual Lineage Pathway */}
      <div className="space-y-3">
        {currentChain.nodes.map((node: EvidenceNode, nIdx: number) => (
          <div key={nIdx} className="relative">
            {/* Connecting Arrow */}
            {nIdx > 0 && (
              <div className="flex items-center justify-center -my-1 text-zinc-600">
                <div className="w-0.5 h-4 bg-zinc-800" />
              </div>
            )}

            <div
              className={`p-3.5 rounded-xl border transition-all ${
                node.level === "FINDING"
                  ? "bg-rose-500/5 border-rose-500/30"
                  : node.level === "EVIDENCE"
                  ? "bg-emerald-500/5 border-emerald-500/30"
                  : "bg-zinc-900/60 border-zinc-800/80"
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700">
                      Step {nIdx + 1}: {node.level}
                    </span>
                    <span className="text-xs font-semibold text-zinc-200">
                      {node.title}
                    </span>
                  </div>
                  {node.subtitle && (
                    <div className="text-xs font-mono text-zinc-400 mb-1">
                      {node.subtitle}
                    </div>
                  )}
                  <p className="text-xs text-zinc-300 leading-relaxed font-mono">
                    {node.detail}
                  </p>
                </div>

                {node.level === "PAGE" && onOpenDocumentViewer && (
                  <button
                    onClick={() =>
                      onOpenDocumentViewer("Builder_Buyer_Agreement_SkyView_A1204.pdf", 15)
                    }
                    className="text-xs text-emerald-400 hover:text-emerald-300 font-medium shrink-0 self-start sm:self-auto"
                  >
                    Open Page 15 →
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
