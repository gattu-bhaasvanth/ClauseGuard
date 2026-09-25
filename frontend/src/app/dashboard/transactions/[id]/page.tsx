"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  FileText,
  AlertTriangle,
  Split,
  Calendar,
  Layers,
  ArrowUpRight,
  Download,
  Share2,
  CheckCircle2,
  Eye,
  ShieldCheck,
  Sparkles,
  Compass,
  GitBranch,
  Bot,
} from "lucide-react";
import { MOCK_SKYVIEW_TRANSACTION, MOCK_COMMAND_CENTER_DATA, MOCK_TIMELINE_DATA } from "@/mock/demoData";
import { Transaction } from "@/types/transaction";
import { PropertySummaryCard } from "@/components/transactions/PropertySummaryCard";
import { InconsistencyCard } from "@/components/transactions/InconsistencyCard";
import { RiskCard } from "@/components/transactions/RiskCard";
import { ObligationTimeline } from "@/components/transactions/ObligationTimeline";
import { DocumentTable } from "@/components/documents/DocumentTable";
import { TransactionHealthScore } from "@/components/dashboard/TransactionHealthScore";
import { SemanticExplorationWorkspace } from "@/components/transactions/SemanticExplorationWorkspace";
import { TransactionCommandCenter } from "@/components/copilot/TransactionCommandCenter";
import { TransactionCopilotPanel } from "@/components/copilot/TransactionCopilotPanel";
import { ExplainableRiskDrawer } from "@/components/copilot/ExplainableRiskDrawer";
import { IntelligentTimeline } from "@/components/copilot/IntelligentTimeline";
import { EvidenceLineageGraph } from "@/components/copilot/EvidenceLineageGraph";
import { TransactionBriefModal } from "@/components/copilot/TransactionBriefModal";
import { LegalDisclaimerNotice } from "@/components/shared/LegalDisclaimerNotice";
import { ProcessingStatusPipeline } from "@/components/shared/ProcessingStatusPipeline";
import { fetchCommandCenter, fetchTimeline, fetchTransactionById } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

export default function TransactionOverviewPage({
  params,
}: {
  params: { id: string };
}) {
  const transactionId = params.id || "skyview-a1204";
  const [transaction, setTransaction] = useState<Transaction | any>(
    transactionId === "skyview-a1204" ? MOCK_SKYVIEW_TRANSACTION : null
  );
  const [isLoading, setIsLoading] = useState(transactionId !== "skyview-a1204");

  const [activeTab, setActiveTab] = useState<
    "command-center" | "timeline" | "lineage" | "inconsistencies" | "risks" | "documents" | "rag"
  >("command-center");

  // Phase 10 Modals & Drawers
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [isBriefModalOpen, setIsBriefModalOpen] = useState(false);
  const [explainFindingId, setExplainFindingId] = useState<string | null>(null);

  // Phase 8 RAG Modal (Preserved)
  const [isAskModalOpen, setIsAskModalOpen] = useState(false);

  // Command Center & Timeline Data
  const [commandCenterData, setCommandCenterData] = useState<any>(
    transactionId === "skyview-a1204" ? MOCK_COMMAND_CENTER_DATA : null
  );
  const [timelineData, setTimelineData] = useState<any>(
    transactionId === "skyview-a1204" ? MOCK_TIMELINE_DATA : null
  );

  useEffect(() => {
    if (transactionId === "skyview-a1204") {
      setTransaction(MOCK_SKYVIEW_TRANSACTION);
      setCommandCenterData(MOCK_COMMAND_CENTER_DATA);
      setTimelineData(MOCK_TIMELINE_DATA);
      setIsLoading(false);
    } else {
      setIsLoading(true);
      fetchTransactionById(transactionId)
        .then((res) => {
          if (res) {
            setTransaction(res);
            if (typeof window !== "undefined") {
              const proj = res.property?.project || res.property?.projectName || "";
              const unt = res.property?.unit || res.property?.unitNumber || "";
              const title = proj && unt ? `${proj} — ${unt}` : (res.title || "Custom Transaction");
              window.dispatchEvent(new CustomEvent("cg-tx-loaded", { detail: { id: res.id, title } }));
            }
          }
        })
        .catch(() => {})
        .finally(() => setIsLoading(false));

      fetchCommandCenter(transactionId)
        .then((res) => {
          if (res) setCommandCenterData(res);
        })
        .catch(() => {});

      fetchTimeline(transactionId)
        .then((res) => {
          if (res) setTimelineData(res);
        })
        .catch(() => {});
    }
  }, [transactionId]);

  // Global Cmd+K / Ctrl+K keyboard shortcut to toggle Copilot
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setIsCopilotOpen((prev) => !prev);
      }
      if (e.key === "Escape") {
        if (isCopilotOpen) setIsCopilotOpen(false);
        if (isBriefModalOpen) setIsBriefModalOpen(false);
        if (explainFindingId) setExplainFindingId(null);
        if (isAskModalOpen) setIsAskModalOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isCopilotOpen, isBriefModalOpen, explainFindingId, isAskModalOpen]);

  const effectiveCommandCenterData = commandCenterData || {
    bundleId: transaction?.id || transactionId,
    projectName: transaction?.property?.project || "Custom Transaction",
    unitNumber: transaction?.property?.unit || "Unit",
    developerName: transaction?.property?.developer || "Developer",
    healthScore: transaction?.healthScore || 85,
    riskLevel: "LOW",
    financialExposure: {
      totalFinancialAtRisk: 0,
      totalFinancialAtRiskFormatted: "₹0",
      baseConsideration: transaction?.property?.salePrice || 0,
      baseConsiderationFormatted: "₹0",
      earnestMoneyForfeitRisk: 0,
      earnestMoneyForfeitRiskFormatted: "₹0",
      statutoryForfeitLimit: 0,
      statutoryForfeitLimitFormatted: "₹0",
      excessForfeitExposure: 0,
      excessForfeitExposureFormatted: "₹0",
      delayInterestRateBuyer: 0,
      delayCompensationRateDeveloper: 0,
      monthlyAsymmetryCost: 0,
      monthlyAsymmetryCostFormatted: "₹0 / mo",
      areaDiscrepancyCostImpact: 0,
      areaDiscrepancyCostImpactFormatted: "₹0",
    },
    riskVectors: [],
    priorityActions: [],
    missingDocumentsCount: 0,
    totalDocumentsCount: transaction?.documentsCount || 0,
    totalClausesAnalyzed: transaction?.clauses?.length || 0,
    totalFindingsCount: transaction?.issuesCount || 0,
  };

  const effectiveTimelineData = timelineData || {
    bundleId: transaction?.id || transactionId,
    events: [],
    totalEvents: 0,
    conflictingEventsCount: 0,
    contractualEventsCount: 0,
    marketingEventsCount: 0,
    inferredEventsCount: 0,
    uncertainEventsCount: 0,
  };

  if (isLoading || !transaction) {
    return (
      <div className="flex items-center justify-center min-h-[460px] p-4">
        <ProcessingStatusPipeline
          currentStage="VERIFYING"
          title="Loading Transaction Intelligence"
          subtitle="Hydrating unified transaction model, verified citations & copilot lineage"
          className="w-full max-w-xl shadow-2xl border-emerald-500/20"
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Project Title & Primary Action */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-surface-border">
        <div>
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-subtle border border-surface-border text-zinc-400">
              ID: {transaction.id}
            </span>
            <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 font-medium">
              <CheckCircle2 className="w-3 h-3 text-emerald-400" />
              Transaction Intelligence Copilot Active
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
            {transaction.title || `${transaction.property?.project || "Custom Transaction"} — ${transaction.property?.unit || "Unit"}`}
          </h1>
          <p className="text-xs text-zinc-400 mt-1">
            {transaction.property?.location || "Location not specified"} • Promoter: {transaction.property?.developer || "Promoter not specified"}
          </p>
        </div>

        <div className="flex items-center gap-2.5 flex-wrap">
          {/* Phase 10 Ask Copilot (with Cmd+K shortcut) */}
          <Button
            data-testid="header-ask-copilot-btn"
            variant="emerald"
            size="sm"
            onClick={() => setIsCopilotOpen(true)}
            className="gap-1.5 text-xs shadow-subtle-glow font-semibold"
          >
            <Sparkles className="w-3.5 h-3.5 text-emerald-300" />
            <span>Ask Copilot</span>
            <kbd className="hidden sm:inline-block text-[9px] bg-emerald-700/40 text-zinc-950 font-mono px-1 rounded ml-1">
              ⌘K
            </kbd>
          </Button>

          {/* Phase 8 Ask ClauseGuard RAG Button (Preserved for tests) */}
          <Button
            data-testid="header-ask-clauseguard-btn"
            variant="secondary"
            size="sm"
            onClick={() => {
              setActiveTab("rag");
              setIsAskModalOpen(true);
            }}
            className="gap-1.5 text-xs"
          >
            <Bot className="w-3.5 h-3.5 text-zinc-400" />
            <span>RAG Search</span>
          </Button>

          <Link href={`/dashboard/transactions/${transaction.id}/analysis`}>
            <Button variant="secondary" size="sm" className="gap-1.5 text-xs">
              <Eye className="w-3.5 h-3.5 text-zinc-400" />
              <span>Split Document Viewer</span>
            </Button>
          </Link>

          <Button
            variant="secondary"
            size="sm"
            onClick={() => setIsBriefModalOpen(true)}
            className="gap-1.5 text-xs"
          >
            <FileText className="w-3.5 h-3.5 text-blue-400" />
            <span>Executive Brief</span>
          </Button>
        </div>
      </div>

      {/* Top Metrics Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <Card className="p-4">
          <span className="text-[10px] uppercase font-semibold text-zinc-400 tracking-wider block">
            Documents Analyzed
          </span>
          <span className="text-2xl font-bold font-mono text-zinc-100 mt-1 block">
            {transaction.documentsCount ?? transaction.documents?.length ?? 0}
          </span>
          <span className="text-[11px] text-zinc-500">
            {(transaction.documentsCount ?? transaction.documents?.length ?? 0) === 1
              ? "1 Document Uploaded"
              : "Agreements, Letters & Brochure"}
          </span>
        </Card>

        <Card className="p-4 border-l-4 border-l-rose-500">
          <span className="text-[10px] uppercase font-semibold text-rose-400 tracking-wider block">
            Total Capital At Risk
          </span>
          <span className="text-2xl font-bold font-mono text-rose-300 mt-1 block">
            {effectiveCommandCenterData.financialExposure?.totalFinancialAtRiskFormatted || "₹0"}
          </span>
          <span className="text-[11px] text-rose-400/80">
            {(effectiveCommandCenterData.financialExposure?.totalFinancialAtRisk || 0) > 0
              ? "Earnest Forfeit + Area Disparity"
              : "No Exposure Detected"}
          </span>
        </Card>

        <Card className="p-4 border-l-4 border-l-amber-500">
          <span className="text-[10px] uppercase font-semibold text-amber-400 tracking-wider block">
            Risk & Discrepancies
          </span>
          <span className="text-2xl font-bold font-mono text-amber-400 mt-1 block">
            {transaction.issuesCount ?? 0}
          </span>
          <span className="text-[11px] text-zinc-500">
            {(transaction.inconsistenciesCount ?? transaction.inconsistencies?.length) || 0} Inconsistencies, {(transaction.risksCount ?? transaction.risks?.length) || 0} Risks
          </span>
        </Card>

        <Card className="p-4">
          <span className="text-[10px] uppercase font-semibold text-zinc-400 tracking-wider block">
            Reconciled Milestones
          </span>
          <span className="text-2xl font-bold font-mono text-zinc-100 mt-1 block">
            {effectiveTimelineData.totalEvents ?? 0}
          </span>
          <span className="text-[11px] text-amber-400/90">
            {(effectiveTimelineData.conflictingEventsCount || 0) > 0
              ? `${effectiveTimelineData.conflictingEventsCount} Conflicting Promises`
              : "No Conflicting Promises"}
          </span>
        </Card>
      </div>

      {/* Structured Navigation Tabs */}
      <div className="space-y-4">
        {/* Tab Headers */}
        <div className="flex items-center gap-2 border-b border-surface-border pb-1 overflow-x-auto">
          {[
            {
              id: "command-center",
              label: "Command Center",
              icon: Compass,
              highlight: true,
            },
            {
              id: "timeline",
              label: `Timeline & Obligations (${effectiveTimelineData.totalEvents ?? 0})`,
              icon: Calendar,
            },
            {
              id: "lineage",
              label: "Evidence Lineage Graph",
              icon: GitBranch,
            },
            {
              id: "rag",
              label: "Ask ClauseGuard (RAG)",
              icon: Sparkles,
            },
            {
              id: "inconsistencies",
              label: `Potential Inconsistencies (${(transaction.inconsistenciesCount ?? transaction.inconsistencies?.length) || 0})`,
              icon: Split,
            },
            {
              id: "risks",
              label: `Potential Risks (${(transaction.risksCount ?? transaction.risks?.length) || 0})`,
              icon: AlertTriangle,
            },
            {
              id: "documents",
              label: `Documents (${(transaction.documentsCount ?? transaction.documents?.length) || 0})`,
              icon: FileText,
            },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;

            return (
              <button
                key={tab.id}
                data-testid={tab.id === "rag" ? "tab-ask-clauseguard-btn" : undefined}
                onClick={() => {
                  setActiveTab(tab.id as any);
                  if (tab.id === "rag") {
                    setTimeout(() => {
                      const el = document.getElementById("ask-clauseguard-workspace");
                      if (el) {
                        el.scrollIntoView({ behavior: "smooth", block: "start" });
                        const input = el.querySelector("input");
                        if (input) input.focus();
                      }
                    }, 50);
                  }
                }}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-medium transition-all whitespace-nowrap ${
                  isActive
                    ? "bg-zinc-800 text-white font-semibold border border-zinc-700/80 shadow-sm"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-surface-subtle"
                }`}
              >
                <Icon
                  className={`w-3.5 h-3.5 ${
                    isActive ? "text-emerald-400" : "text-zinc-500"
                  }`}
                />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab 1: Command Center (Phase 10 Cockpit) */}
        {activeTab === "command-center" && (
          <TransactionCommandCenter
            data={effectiveCommandCenterData}
            onOpenCopilot={() => setIsCopilotOpen(true)}
            onOpenBrief={() => setIsBriefModalOpen(true)}
            onOpenTimeline={() => setActiveTab("timeline")}
            onSelectRiskFinding={(id) => setExplainFindingId(id)}
          />
        )}

        {/* Tab 2: Timeline & Obligations (Phase 10 Timeline Intelligence) */}
        {activeTab === "timeline" && (
          <IntelligentTimeline
            timelineData={effectiveTimelineData}
            onInspectDocument={(docName, page) => {
              // Could navigate to Split Document Viewer
            }}
          />
        )}

        {/* Tab 3: Evidence Lineage Graph (Phase 10 Traceability) */}
        {activeTab === "lineage" && (
          <EvidenceLineageGraph bundleId={transaction.id} />
        )}

        {/* Tab 4: Semantic Exploration / RAG Workspace (Phase 8 Preserved) */}
        {activeTab === "rag" && (
          <div id="ask-clauseguard-workspace" data-testid="rag-tab-panel">
            <SemanticExplorationWorkspace transactionId={transaction.id} />
          </div>
        )}

        {/* Tab 5: Inconsistencies (Phase 6 Preserved) */}
        {activeTab === "inconsistencies" && (
          <div className="space-y-4">
            <div className="p-3.5 rounded-lg bg-surface-subtle border border-surface-border text-xs text-zinc-300 flex items-center justify-between">
              <div>
                <span className="font-semibold text-zinc-100 block">
                  Cross-Document Inconsistency Verification
                </span>
                <span className="text-[11px] text-zinc-400">
                  These discrepancies highlight where marketing claims or preliminary letters differ from formal draft contracts.
                </span>
              </div>
              <span className="text-[10px] text-purple-400 font-mono font-semibold">
                Side-by-Side Lineage
              </span>
            </div>

            <div className="space-y-4">
              {(!transaction.inconsistencies || transaction.inconsistencies.length === 0) ? (
                <div className="p-8 rounded-xl bg-surface border border-surface-border text-center text-xs text-zinc-400 space-y-1">
                  <p className="font-semibold text-zinc-300">No cross-document discrepancies detected</p>
                  <p className="text-zinc-500">
                    With a single uploaded document, cross-document comparison is not applicable. Upload additional files (such as marketing brochures or allotment letters) to enable cross-document discrepancy checking.
                  </p>
                </div>
              ) : (
                transaction.inconsistencies.map((inc: any) => (
                  <InconsistencyCard
                    key={inc.id}
                    inconsistency={inc}
                    transactionId={transaction.id}
                  />
                ))
              )}
            </div>
          </div>
        )}

        {/* Tab 6: Potential Risks (Phase 7 Preserved) */}
        {activeTab === "risks" && (
          <div className="space-y-4">
            <div className="p-3.5 rounded-lg bg-surface-subtle border border-surface-border text-xs text-zinc-300">
              <span className="font-semibold text-zinc-100 block">
                Asymmetric Liability & High-Risk Clause Audit
              </span>
              <span className="text-[11px] text-zinc-400">
                Identifies contractual terms where legal or financial obligations are heavily weighted against the purchaser.
              </span>
            </div>

            <div className="space-y-4">
              {(!transaction.risks || transaction.risks.length === 0) ? (
                <div className="p-8 rounded-xl bg-surface border border-surface-border text-center text-xs text-zinc-400 space-y-1">
                  <p className="font-semibold text-zinc-300">No high-priority contractual risks detected</p>
                  <p className="text-zinc-500">
                    No aggressive builder forfeiture or delay compensation asymmetry clauses were flagged for this transaction.
                  </p>
                </div>
              ) : (
                transaction.risks.map((risk: any) => (
                  <div key={risk.id} className="relative">
                    <RiskCard risk={risk} transactionId={transaction.id} />
                    <div className="mt-2 flex justify-end">
                      <button
                        onClick={() => setExplainFindingId(risk.id)}
                        className="text-xs text-emerald-400 hover:text-emerald-300 font-medium inline-flex items-center gap-1 transition-colors"
                      >
                        <span>Why is this risky? (Explainable Analysis)</span>
                        <span>→</span>
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Tab 7: Documents Table (Phase 3 Preserved) */}
        {activeTab === "documents" && (
          <DocumentTable
            documents={transaction.documents || []}
            transactionId={transaction.id}
          />
        )}
      </div>

      {/* Phase 10: Persistent Copilot Panel (Cmd+K) */}
      <TransactionCopilotPanel
        isOpen={isCopilotOpen}
        onClose={() => setIsCopilotOpen(false)}
        bundleId={transaction.id}
        onSelectCitation={(citation) => {
          // Open explainability or document
          if (citation.clauseNumber?.includes("8.2") || citation.clauseNumber?.includes("Penalty")) {
            setExplainFindingId("risk-01");
          }
        }}
      />

      {/* Phase 10: Explainable Risk Intelligence Drawer ("Why is this risky?") */}
      <ExplainableRiskDrawer
        isOpen={Boolean(explainFindingId)}
        onClose={() => setExplainFindingId(null)}
        bundleId={transaction.id}
        findingId={explainFindingId}
      />

      {/* Phase 10: Executive Transaction Brief Modal */}
      <TransactionBriefModal
        isOpen={isBriefModalOpen}
        onClose={() => setIsBriefModalOpen(false)}
        bundleId={transaction.id}
      />

      {/* Phase 8: Interactive Ask ClauseGuard Modal Overlay (Preserved for tests) */}
      {isAskModalOpen && (
        <div
          data-testid="ask-clauseguard-modal-overlay"
          className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/80 backdrop-blur-md animate-in fade-in duration-200"
          onClick={() => setIsAskModalOpen(false)}
        >
          <div
            className="relative w-full max-w-4xl max-h-[92vh] overflow-y-auto rounded-2xl border border-emerald-500/30 bg-surface-card p-4 sm:p-6 shadow-2xl space-y-4 animate-in zoom-in-95 duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            <SemanticExplorationWorkspace
              transactionId={transaction.id}
              isModal={true}
              autoFocusInput={true}
              onClose={() => setIsAskModalOpen(false)}
            />
          </div>
        </div>
      )}

      <LegalDisclaimerNotice variant="banner" />
    </div>
  );
}
