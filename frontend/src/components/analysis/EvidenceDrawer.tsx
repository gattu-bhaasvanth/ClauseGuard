import React from "react";
import { FileText, ShieldAlert, Sparkles, AlertCircle, CheckCircle2 } from "lucide-react";
import { ClauseItem } from "@/types/transaction";
import { Card } from "@/components/ui/Card";
import { SeverityBadge } from "@/components/shared/SeverityBadge";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";

interface EvidenceDrawerProps {
  clause: ClauseItem;
  documentName?: string;
  className?: string;
}

export function EvidenceDrawer({
  clause,
  documentName = "Builder-Buyer Agreement",
  className,
}: EvidenceDrawerProps) {
  return (
    <Card className={cn("p-5 border-surface-border bg-surface flex flex-col justify-between space-y-4", className)}>
      <div>
        {/* Top Header */}
        <div className="flex items-center justify-between pb-3 border-b border-surface-border">
          <div className="flex items-center gap-2">
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
            />
            <span className="text-xs font-semibold text-zinc-100">
              Evidence Inspector
            </span>
          </div>
          <span className="text-[10px] text-zinc-500 font-mono">
            Lineage Anchor
          </span>
        </div>

        {/* Structured Evidence Citation Details */}
        <div className="grid grid-cols-3 gap-2 py-3 border-b border-surface-border/60 text-xs">
          <div>
            <span className="text-[10px] text-zinc-500 uppercase font-semibold tracking-wider block">
              Document
            </span>
            <span className="font-medium text-zinc-200 truncate block">
              {documentName}
            </span>
          </div>

          <div>
            <span className="text-[10px] text-zinc-500 uppercase font-semibold tracking-wider block">
              Page
            </span>
            <span className="font-mono font-medium text-zinc-200">
              {clause.pageNumber}
            </span>
          </div>

          <div>
            <span className="text-[10px] text-zinc-500 uppercase font-semibold tracking-wider block">
              Clause
            </span>
            <span className="font-mono font-semibold text-emerald-400">
              {clause.clauseNumber}
            </span>
          </div>
        </div>

        {/* Raw Evidence Quote Box */}
        <div className="my-3">
          <span className="text-[10px] text-zinc-400 uppercase tracking-wider font-semibold block mb-1.5">
            Exact Raw Document Evidence
          </span>
          <div className="p-3.5 rounded-lg bg-surface-subtle border border-surface-border text-xs text-zinc-200 font-serif leading-relaxed italic border-l-2 border-l-emerald-500">
            &ldquo;{clause.fullExcerpt}&rdquo;
          </div>
        </div>

        {/* Finding Summary */}
        <div className="space-y-1.5 text-xs">
          <span className="text-[10px] text-zinc-400 uppercase tracking-wider font-semibold block">
            Analysis & Potential Impact
          </span>
          <p className="text-zinc-300 leading-relaxed text-xs">
            {clause.analysisSummary}
          </p>
          {clause.riskDetails && (
            <p className="text-amber-400/90 text-[11px] leading-relaxed">
              <strong>Caveat:</strong> {clause.riskDetails}
            </p>
          )}
        </div>
      </div>

      {/* Demo Notice Banner */}
      <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 text-[11px] text-zinc-400 flex items-start gap-2">
        <AlertCircle className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
        <div>
          <span className="text-zinc-300 font-medium block">
            Demo UI Simulation (Phase 1)
          </span>
          <p className="text-[10px] text-zinc-500 leading-tight">
            In subsequent phases, this evidence connects directly to live backend OCR text coordinates and vector search embeddings.
          </p>
        </div>
      </div>
    </Card>
  );
}
