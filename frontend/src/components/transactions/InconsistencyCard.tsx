import React from "react";
import Link from "next/link";
import { ArrowRight, FileText, Split, ExternalLink } from "lucide-react";
import { InconsistencyFinding } from "@/types/transaction";
import { Card } from "@/components/ui/Card";
import { SeverityBadge } from "@/components/shared/SeverityBadge";
import { Button } from "@/components/ui/Button";

interface InconsistencyCardProps {
  inconsistency: InconsistencyFinding;
  transactionId?: string;
}

export function InconsistencyCard({
  inconsistency,
  transactionId = "skyview-a1204",
}: InconsistencyCardProps) {
  const { primaryEvidence, secondaryEvidence } = inconsistency;

  return (
    <Card className="p-5 border-l-4 border-l-purple-500/80 hover:border-zinc-700/90 hover:shadow-lg hover:shadow-purple-950/20 hover:-translate-y-0.5 transition-all duration-200 ease-out">
      {/* Header with Type and Severity */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2">
          <SeverityBadge type="POTENTIAL_INCONSISTENCY" />
          <span className="text-xs font-semibold text-zinc-300">
            {inconsistency.title}
          </span>
          <span className="text-[10px] text-zinc-500 font-mono">
            [{inconsistency.category}]
          </span>
        </div>

        <Link
          href={`/dashboard/transactions/${transactionId}/analysis?clause=${secondaryEvidence.clauseNumber || ""}`}
        >
          <Button variant="ghost" size="sm" className="h-7 text-xs gap-1 text-purple-400 hover:text-purple-300">
            <span>Inspect in Viewer</span>
            <ExternalLink className="w-3 h-3" />
          </Button>
        </Link>
      </div>

      {/* Description */}
      <p className="text-xs text-zinc-300 mb-4 leading-relaxed">
        {inconsistency.description}
      </p>

      {/* Side-by-Side Evidence Comparison Container */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
        {/* Document A (e.g. Brochure / Allotment) */}
        <div className="rounded-lg bg-surface-subtle p-3.5 border border-surface-border flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-[11px] font-semibold text-zinc-400 mb-1.5">
              <span className="flex items-center gap-1.5 text-zinc-200 truncate">
                <FileText className="w-3.5 h-3.5 text-zinc-400 flex-shrink-0" />
                <span className="truncate">{primaryEvidence.documentName}</span>
              </span>
              <span className="text-zinc-500 font-mono text-[10px] flex-shrink-0">
                Page {primaryEvidence.pageNumber}
              </span>
            </div>

            <blockquote className="text-[11px] text-zinc-300 italic border-l-2 border-zinc-600 pl-2.5 my-2 leading-relaxed">
              &ldquo;{primaryEvidence.excerpt}&rdquo;
            </blockquote>
          </div>

          <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold mt-2">
            Representation Source
          </div>
        </div>

        {/* Document B (e.g. Agreement for Sale / BBA) */}
        <div className="rounded-lg bg-purple-950/20 p-3.5 border border-purple-500/30 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-[11px] font-semibold text-purple-200 mb-1.5">
              <span className="flex items-center gap-1.5 text-purple-300 truncate">
                <FileText className="w-3.5 h-3.5 text-purple-400 flex-shrink-0" />
                <span className="truncate">{secondaryEvidence.documentName}</span>
              </span>
              <span className="text-purple-400/80 font-mono text-[10px] flex-shrink-0">
                {secondaryEvidence.clauseNumber || `Page ${secondaryEvidence.pageNumber}`}
              </span>
            </div>

            <blockquote className="text-[11px] text-purple-200 italic border-l-2 border-purple-500/60 pl-2.5 my-2 leading-relaxed">
              &ldquo;{secondaryEvidence.excerpt}&rdquo;
            </blockquote>
          </div>

          <div className="text-[10px] text-purple-400 uppercase tracking-wider font-semibold mt-2">
            Binding Contractual Term
          </div>
        </div>
      </div>
    </Card>
  );
}
