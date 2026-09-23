"use client";

import React from "react";
import { Filter, ArrowRight, ShieldAlert, Sparkles } from "lucide-react";
import { ClauseItem } from "@/types/transaction";
import { SeverityBadge } from "@/components/shared/SeverityBadge";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/utils";

interface ClauseListProps {
  clauses: ClauseItem[];
  selectedClauseId: string;
  onSelectClause: (clause: ClauseItem) => void;
  className?: string;
}

export function ClauseList({
  clauses,
  selectedClauseId,
  onSelectClause,
  className,
}: ClauseListProps) {
  return (
    <div className={cn("flex flex-col h-full space-y-3", className)}>
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-zinc-100">
            Detected Clauses & Findings
          </h3>
          <p className="text-xs text-zinc-400">
            Select a clause to inspect exact evidence in the document viewer
          </p>
        </div>
        <span className="text-[10px] text-zinc-500 font-mono px-2 py-0.5 rounded bg-surface-subtle border border-surface-border">
          {clauses.length} items
        </span>
      </div>

      {/* Clause items list */}
      <div className="space-y-2 overflow-y-auto pr-1 flex-1">
        {clauses.map((clause) => {
          const isSelected = selectedClauseId === clause.id;

          return (
            <div
              key={clause.id}
              onClick={() => onSelectClause(clause)}
              className={cn(
                "p-3.5 rounded-lg border text-xs cursor-pointer transition-all duration-150 flex flex-col justify-between gap-2",
                isSelected
                  ? "bg-zinc-800/90 border-emerald-500 shadow-md ring-1 ring-emerald-500/30"
                  : "bg-surface-subtle/80 border-surface-border hover:bg-surface-subtle hover:border-zinc-700"
              )}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="font-semibold text-zinc-200 font-mono">
                  {clause.clauseNumber}
                </span>
                <SeverityBadge
                  type={
                    clause.status === "RISK"
                      ? clause.severity || "HIGH"
                      : clause.status === "INCONSISTENCY"
                      ? "POTENTIAL_INCONSISTENCY"
                      : clause.status === "REVIEW_REQUIRED"
                      ? "REVIEW_REQUIRED"
                      : "VERIFIED"
                  }
                  size="sm"
                />
              </div>

              <div>
                <h4 className="font-medium text-zinc-100 mb-0.5">
                  {clause.title}
                </h4>
                <p className="text-[11px] text-zinc-400 line-clamp-2 leading-relaxed">
                  {clause.analysisSummary}
                </p>
              </div>

              <div className="flex items-center justify-between text-[10px] text-zinc-500 pt-1 border-t border-surface-border/40">
                <span>{clause.category}</span>
                <span className="font-mono">Page {clause.pageNumber}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
