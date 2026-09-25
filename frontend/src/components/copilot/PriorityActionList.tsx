"use client";

import React from "react";
import { PriorityActionItem } from "@/types/copilot";
import { CheckCircle2, ChevronRight, FileText, ArrowUpRight } from "lucide-react";

interface PriorityActionListProps {
  actions: PriorityActionItem[];
  onSelectAction?: (action: PriorityActionItem) => void;
}

const CATEGORY_LABELS: Record<string, { label: string; style: string }> = {
  NEGOTIATION: { label: "Clause Negotiation", style: "bg-purple-500/10 text-purple-300 border-purple-500/20" },
  DOCUMENT_REQUEST: { label: "Document Request", style: "bg-blue-500/10 text-blue-300 border-blue-500/20" },
  LEGAL_REVIEW: { label: "Counsel Review", style: "bg-amber-500/10 text-amber-300 border-amber-500/20" },
  PAYMENT_HOLD: { label: "Payment Hold", style: "bg-rose-500/10 text-rose-300 border-rose-500/20" },
};

const SEVERITY_BADGES: Record<string, string> = {
  CRITICAL: "bg-rose-500/10 text-rose-400 border-rose-500/30",
  HIGH: "bg-amber-500/10 text-amber-400 border-amber-500/30",
  MEDIUM: "bg-blue-500/10 text-blue-400 border-blue-500/30",
  LOW: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
};

export const PriorityActionList: React.FC<PriorityActionListProps> = ({
  actions,
  onSelectAction,
}) => {
  const actionItems = actions || [];

  return (
    <div className="rounded-xl bg-[#111622]/90 border border-zinc-800/90 p-5 shadow-lg">
      <div className="flex items-center justify-between pb-4 border-b border-zinc-800/80 mb-4">
        <div>
          <h3 className="text-base font-semibold text-zinc-100">
            Priority Action Items Before Contract Execution
          </h3>
          <p className="text-xs text-zinc-400 mt-0.5">
            Ranked legal amendments and verification requests for buyer legal counsel
          </p>
        </div>
        <span className="text-xs font-mono font-medium text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
          {actionItems.length} Action Items
        </span>
      </div>

      <div className="space-y-3">
        {actionItems.length === 0 ? (
          <div className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800 text-center text-xs text-zinc-400">
            No priority action items required at this stage. All uploaded documents verified.
          </div>
        ) : (
          actionItems.map((act, index) => {
          const cat = CATEGORY_LABELS[act.category] || { label: act.category, style: "bg-zinc-800 text-zinc-300 border-zinc-700" };
          const sev = SEVERITY_BADGES[act.severity] || SEVERITY_BADGES.MEDIUM;

          return (
            <div
              key={act.id}
              onClick={() => onSelectAction?.(act)}
              className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800/70 hover:border-zinc-700 hover:bg-zinc-900/90 transition-all duration-200 cursor-pointer group"
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  onSelectAction?.(act);
                }
              }}
            >
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                <div className="flex items-start gap-3">
                  <span className="font-mono text-xs font-semibold text-zinc-400 mt-0.5">
                    #{index + 1}
                  </span>
                  <div>
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded border ${sev}`}>
                        {act.severity}
                      </span>
                      <span className={`text-[10px] font-medium px-2 py-0.5 rounded border ${cat.style}`}>
                        {cat.label}
                      </span>
                      {act.clauseReference && (
                        <span className="text-[11px] font-mono text-zinc-400 bg-zinc-800/80 px-2 py-0.5 rounded">
                          {act.clauseReference}
                        </span>
                      )}
                    </div>
                    <h4 className="text-sm font-semibold text-zinc-100 group-hover:text-emerald-400 transition-colors">
                      {act.title}
                    </h4>
                    <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
                      {act.description}
                    </p>
                  </div>
                </div>

                <div className="shrink-0 sm:self-center">
                  <span className="inline-flex items-center gap-1 text-xs font-medium text-emerald-400 group-hover:translate-x-0.5 transition-transform">
                    <span>Inspect</span>
                    <ChevronRight className="w-4 h-4" />
                  </span>
                </div>
              </div>

              {/* Recommended Action Box */}
              <div className="mt-3 p-2.5 rounded-lg bg-emerald-950/20 border border-emerald-900/30 text-xs text-emerald-300/90 flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold text-emerald-300">Recommended Action: </span>
                  <span>{act.recommendedAction}</span>
                </div>
              </div>
            </div>
          );
        }))}
      </div>
    </div>
  );
};
