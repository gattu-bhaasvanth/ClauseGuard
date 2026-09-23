import React from "react";
import Link from "next/link";
import { FileText, ExternalLink, Lightbulb } from "lucide-react";
import { RiskFinding } from "@/types/transaction";
import { Card } from "@/components/ui/Card";
import { SeverityBadge } from "@/components/shared/SeverityBadge";
import { Button } from "@/components/ui/Button";

interface RiskCardProps {
  risk: RiskFinding;
  transactionId?: string;
}

export function RiskCard({ risk, transactionId = "skyview-a1204" }: RiskCardProps) {
  const { citation } = risk;

  return (
    <Card className="p-5 hover:border-zinc-700 transition-all">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2 flex-wrap">
          <SeverityBadge type={risk.severity} />
          <span className="text-xs font-semibold text-zinc-100">
            {risk.title}
          </span>
          <span className="text-[10px] text-zinc-400 font-mono">
            [{risk.clauseType}]
          </span>
        </div>

        <Link
          href={`/dashboard/transactions/${transactionId}/analysis?clause=${citation.clauseNumber || ""}`}
        >
          <Button variant="ghost" size="sm" className="h-7 text-xs gap-1 text-zinc-400 hover:text-zinc-200">
            <span>View Clause</span>
            <ExternalLink className="w-3 h-3" />
          </Button>
        </Link>
      </div>

      {/* Impact summary */}
      <p className="text-xs font-medium text-rose-300/90 mb-2">
        {risk.impact}
      </p>

      {/* Explanation */}
      <p className="text-xs text-zinc-400 mb-4 leading-relaxed">
        {risk.explanation}
      </p>

      {/* Citation Box */}
      <div className="rounded-lg bg-surface-subtle p-3 border border-surface-border mb-3 text-xs">
        <div className="flex items-center justify-between text-[11px] text-zinc-400 mb-1.5 font-medium">
          <span className="flex items-center gap-1.5 text-zinc-300 truncate">
            <FileText className="w-3.5 h-3.5 text-zinc-500 flex-shrink-0" />
            <span className="truncate">{citation.documentName}</span>
          </span>
          <span className="font-mono text-zinc-500 text-[10px]">
            {citation.clauseNumber} • Page {citation.pageNumber}
          </span>
        </div>

        <blockquote className="text-[11px] text-zinc-300 italic border-l-2 border-zinc-700 pl-2.5 my-1 leading-relaxed">
          &ldquo;{citation.excerpt}&rdquo;
        </blockquote>
      </div>

      {/* Recommendation informational Note */}
      {risk.recommendationNote && (
        <div className="flex items-start gap-2 p-2.5 rounded-md bg-amber-500/5 border border-amber-500/20 text-[11px] text-amber-300/90 leading-normal">
          <Lightbulb className="w-3.5 h-3.5 text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-amber-300">Informational Note: </span>
            <span>{risk.recommendationNote}</span>
          </div>
        </div>
      )}
    </Card>
  );
}
