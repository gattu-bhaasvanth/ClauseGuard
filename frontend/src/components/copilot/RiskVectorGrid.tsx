"use client";

import React from "react";
import { RiskVectorItem } from "@/types/copilot";
import { AlertTriangle, ShieldAlert, Clock, Maximize2, FileCheck2 } from "lucide-react";

interface RiskVectorGridProps {
  riskVectors: RiskVectorItem[];
  onSelectVector?: (vectorId: string) => void;
}

const VECTOR_ICONS: Record<string, React.ReactNode> = {
  financial_exposure: <AlertTriangle className="w-5 h-5 text-rose-400" />,
  contractual_asymmetry: <ShieldAlert className="w-5 h-5 text-rose-400" />,
  timeline_delivery: <Clock className="w-5 h-5 text-amber-400" />,
  dimensional_variance: <Maximize2 className="w-5 h-5 text-amber-400" />,
  document_completeness: <FileCheck2 className="w-5 h-5 text-blue-400" />,
};

const SEVERITY_COLORS: Record<string, { badge: string; border: string }> = {
  CRITICAL: {
    badge: "bg-rose-500/10 text-rose-400 border-rose-500/20",
    border: "border-rose-500/30 hover:border-rose-500/50",
  },
  HIGH: {
    badge: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    border: "border-amber-500/30 hover:border-amber-500/50",
  },
  MEDIUM: {
    badge: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
    border: "border-yellow-500/30 hover:border-yellow-500/50",
  },
  LOW: {
    badge: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    border: "border-emerald-500/30 hover:border-emerald-500/50",
  },
};

export const RiskVectorGrid: React.FC<RiskVectorGridProps> = ({
  riskVectors,
  onSelectVector,
}) => {
  const vectors = riskVectors || [];

  if (vectors.length === 0) {
    return (
      <div className="p-4 rounded-xl bg-[#111622]/80 border border-zinc-800 text-center text-xs text-zinc-400">
        No high-risk vectors flagged. All verified parameters within standard statutory thresholds.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3.5">
      {vectors.map((v) => {
        const colors = SEVERITY_COLORS[v.riskLevel] || SEVERITY_COLORS.MEDIUM;
        const icon = VECTOR_ICONS[v.id] || <AlertTriangle className="w-5 h-5 text-amber-400" />;

        return (
          <div
            key={v.id}
            onClick={() => onSelectVector?.(v.id)}
            className={`flex flex-col justify-between p-4 rounded-xl bg-[#111622]/80 border ${colors.border} transition-all duration-200 hover:bg-[#141b2b] cursor-pointer group`}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onSelectVector?.(v.id);
              }
            }}
          >
            <div>
              <div className="flex items-center justify-between gap-2 mb-2.5">
                <div className="p-2 rounded-lg bg-zinc-900/80 border border-zinc-800 group-hover:scale-105 transition-transform">
                  {icon}
                </div>
                <span
                  className={`text-[11px] font-mono font-semibold px-2 py-0.5 rounded-full border ${colors.badge}`}
                >
                  {v.riskLevel}
                </span>
              </div>
              <h4 className="text-sm font-semibold text-zinc-100 mb-1.5 leading-snug group-hover:text-emerald-400 transition-colors">
                {v.name}
              </h4>
              <p className="text-xs text-zinc-400 leading-relaxed line-clamp-3">
                {v.primaryConcern}
              </p>
            </div>

            <div className="mt-4 pt-3 border-t border-zinc-800/80">
              {v.quantifiedStat && (
                <div className="text-[11px] font-mono text-zinc-300 bg-zinc-900/60 px-2 py-1 rounded border border-zinc-800/60 mb-2 truncate">
                  {v.quantifiedStat}
                </div>
              )}
              <div className="flex items-center justify-between text-xs text-zinc-400">
                <span>Vector Health</span>
                <span className="font-mono font-medium text-zinc-200">
                  {v.score}/100
                </span>
              </div>
              <div className="w-full bg-zinc-800/70 h-1.5 rounded-full overflow-hidden mt-1.5">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    v.score >= 70
                      ? "bg-emerald-500"
                      : v.score >= 50
                      ? "bg-amber-500"
                      : "bg-rose-500"
                  }`}
                  style={{ width: `${Math.max(8, v.score)}%` }}
                />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
