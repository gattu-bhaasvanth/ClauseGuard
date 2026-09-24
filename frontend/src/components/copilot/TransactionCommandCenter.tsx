"use client";

import React from "react";
import { TransactionCommandCenterData, PriorityActionItem } from "@/types/copilot";
import { RiskVectorGrid } from "./RiskVectorGrid";
import { FinancialExposureCard } from "./FinancialExposureCard";
import { PriorityActionList } from "./PriorityActionList";
import { Sparkles, Calendar, FileText, ShieldAlert, CheckCircle, FileSpreadsheet } from "lucide-react";

interface TransactionCommandCenterProps {
  data: TransactionCommandCenterData;
  onOpenCopilot: () => void;
  onOpenBrief: () => void;
  onOpenTimeline: () => void;
  onSelectRiskFinding: (findingId: string) => void;
}

export const TransactionCommandCenter: React.FC<TransactionCommandCenterProps> = ({
  data,
  onOpenCopilot,
  onOpenBrief,
  onOpenTimeline,
  onSelectRiskFinding,
}) => {
  const handleSelectAction = (action: PriorityActionItem) => {
    // If the action references penalty or area, open corresponding finding
    if (action.id === "act-01" || action.id === "act-02") {
      onSelectRiskFinding("risk-01");
    } else if (action.id === "act-03") {
      onSelectRiskFinding("inc-02");
    } else if (action.id === "act-04") {
      onSelectRiskFinding("inc-01");
    } else {
      onOpenCopilot();
    }
  };

  const handleSelectVector = (vectorId: string) => {
    if (vectorId === "timeline_delivery") {
      onOpenTimeline();
    } else if (vectorId === "contractual_asymmetry" || vectorId === "financial_exposure") {
      onSelectRiskFinding("risk-01");
    } else if (vectorId === "dimensional_variance") {
      onSelectRiskFinding("inc-01");
    } else {
      onOpenCopilot();
    }
  };

  return (
    <div className="space-y-6">
      {/* Hero Executive Header */}
      <div className="rounded-2xl bg-gradient-to-r from-[#121622] via-[#10141d] to-[#0d1017] border border-zinc-800 p-6 shadow-xl relative overflow-hidden">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-mono font-medium px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Phase 10: Transaction Intelligence Active
              </span>
              <span className="text-xs font-mono text-zinc-400">
                Bundle ID: {data.bundleId}
              </span>
            </div>
            <h1 className="text-2xl font-bold text-zinc-100 tracking-tight">
              {data.projectName} — {data.unitNumber}
            </h1>
            <p className="text-sm text-zinc-400 mt-1">
              Developer: <span className="text-zinc-200 font-medium">{data.developerName}</span> • Analyzed {data.totalDocumentsCount} documents & {data.totalClausesAnalyzed} contractual clauses
            </p>
          </div>

          {/* Quick Action Buttons */}
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={onOpenCopilot}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-zinc-950 font-semibold text-xs shadow-lg shadow-emerald-500/10 transition-all active:scale-95"
            >
              <Sparkles className="w-4 h-4" />
              <span>Ask Copilot</span>
              <kbd className="hidden sm:inline-block text-[10px] bg-emerald-600/30 text-zinc-950 font-mono px-1.5 py-0.5 rounded">
                ⌘K
              </kbd>
            </button>

            <button
              onClick={onOpenTimeline}
              className="inline-flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-zinc-900/90 hover:bg-zinc-800 text-zinc-200 hover:text-white border border-zinc-700/80 font-medium text-xs transition-all active:scale-95"
            >
              <Calendar className="w-4 h-4 text-amber-400" />
              <span>Timeline & Obligations</span>
            </button>

            <button
              onClick={onOpenBrief}
              className="inline-flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-zinc-900/90 hover:bg-zinc-800 text-zinc-200 hover:text-white border border-zinc-700/80 font-medium text-xs transition-all active:scale-95"
            >
              <FileText className="w-4 h-4 text-blue-400" />
              <span>Executive Brief</span>
            </button>
          </div>
        </div>
      </div>

      {/* 5 Risk Vectors */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-400">
            Multi-Dimensional Risk Vectors
          </h2>
          <span className="text-xs text-zinc-400">
            Click any vector to inspect evidence
          </span>
        </div>
        <RiskVectorGrid
          riskVectors={data.riskVectors}
          onSelectVector={handleSelectVector}
        />
      </div>

      {/* Financial Exposure Card */}
      <FinancialExposureCard
        financial={data.financialExposure}
        onExploreExposure={() => onSelectRiskFinding("risk-01")}
      />

      {/* Priority Actions */}
      <PriorityActionList
        actions={data.priorityActions}
        onSelectAction={handleSelectAction}
      />
    </div>
  );
};
