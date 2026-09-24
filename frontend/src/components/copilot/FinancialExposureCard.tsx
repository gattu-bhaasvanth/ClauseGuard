"use client";

import React from "react";
import { FinancialExposureBreakdown } from "@/types/copilot";
import { DollarSign, TrendingUp, AlertOctagon, Scale, ShieldCheck } from "lucide-react";

interface FinancialExposureCardProps {
  financial: FinancialExposureBreakdown;
  onExploreExposure?: () => void;
}

export const FinancialExposureCard: React.FC<FinancialExposureCardProps> = ({
  financial,
  onExploreExposure,
}) => {
  return (
    <div className="rounded-xl bg-[#111622]/90 border border-zinc-800/90 p-5 shadow-lg relative overflow-hidden">
      {/* Background subtle radial glow */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-rose-500/5 rounded-full blur-3xl pointer-events-none" />

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-zinc-800/80">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <AlertOctagon className="w-5 h-5 text-rose-400" />
            <h3 className="text-base font-semibold text-zinc-100">
              Quantified Financial Exposure Matrix
            </h3>
          </div>
          <p className="text-xs text-zinc-400">
            Computed asymmetric liability, earnest money cancellation risk, and valuation disparity
          </p>
        </div>

        <div className="flex items-baseline gap-2 bg-rose-500/10 border border-rose-500/25 px-3.5 py-2 rounded-xl">
          <span className="text-xs text-rose-400 font-medium uppercase tracking-wide">
            Total Capital At Risk:
          </span>
          <span className="text-xl font-bold font-mono text-rose-300">
            {financial.totalFinancialAtRiskFormatted}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
        {/* Metric 1: Consideration & Deposit */}
        <div className="p-3.5 rounded-lg bg-zinc-900/60 border border-zinc-800/70">
          <span className="text-xs text-zinc-400 block mb-1">Base Consideration</span>
          <span className="text-lg font-bold font-mono text-zinc-100 block">
            {financial.baseConsiderationFormatted}
          </span>
          <div className="mt-2 flex items-center gap-1.5 text-[11px] text-zinc-400">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span>Agreed Unit Price (BBA)</span>
          </div>
        </div>

        {/* Metric 2: Earnest Money Forfeiture Risk */}
        <div className="p-3.5 rounded-lg bg-rose-950/20 border border-rose-900/30">
          <span className="text-xs text-rose-300 block mb-1">Earnest Forfeiture (20%)</span>
          <span className="text-lg font-bold font-mono text-rose-300 block">
            {financial.earnestMoneyForfeitRiskFormatted}
          </span>
          <div className="mt-2 text-[11px] text-rose-400/90 font-mono">
            +{financial.excessForfeitExposureFormatted} excess vs 10% RERA limit
          </div>
        </div>

        {/* Metric 3: Penalty Disparity */}
        <div className="p-3.5 rounded-lg bg-amber-950/20 border border-amber-900/30">
          <span className="text-xs text-amber-300 block mb-1">Penalty Imbalance</span>
          <div className="flex items-baseline gap-1.5 text-base font-bold font-mono text-amber-200">
            <span>{financial.delayInterestRateBuyer}%</span>
            <span className="text-xs font-normal text-zinc-400">buyer vs</span>
            <span>{financial.delayCompensationRateDeveloper}%</span>
            <span className="text-xs font-normal text-zinc-400">dev</span>
          </div>
          <div className="mt-2 text-[11px] text-amber-400/90 font-mono">
            {financial.monthlyAsymmetryCostFormatted} asymmetry
          </div>
        </div>

        {/* Metric 4: Area Valuation Deficit */}
        <div className="p-3.5 rounded-lg bg-zinc-900/60 border border-zinc-800/70">
          <span className="text-xs text-zinc-400 block mb-1">Carpet Area Shortfall Cost</span>
          <span className="text-lg font-bold font-mono text-zinc-100 block">
            {financial.areaDiscrepancyCostImpactFormatted}
          </span>
          <div className="mt-2 text-[11px] text-zinc-400">
            70 sq.ft (-4.8%) @ effective rate
          </div>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-zinc-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-zinc-400">
        <div className="flex items-center gap-2">
          <Scale className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>
            Statutory Benchmark: RERA Section 13 restricts booking earnest deposit to 10% maximum.
          </span>
        </div>
        {onExploreExposure && (
          <button
            onClick={onExploreExposure}
            className="text-emerald-400 hover:text-emerald-300 font-medium inline-flex items-center gap-1 transition-colors self-start sm:self-auto"
          >
            <span>Explain Financial Risks</span>
            <span>→</span>
          </button>
        )}
      </div>
    </div>
  );
};
