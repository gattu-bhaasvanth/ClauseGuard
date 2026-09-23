import React from "react";
import { ShieldCheck, AlertTriangle, HelpCircle } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/utils";

interface TransactionHealthScoreProps {
  score: number;
  totalClauses?: number;
  verifiedCount?: number;
  reviewCount?: number;
  criticalCount?: number;
  className?: string;
}

export function TransactionHealthScore({
  score,
  totalClauses = 24,
  verifiedCount = 18,
  reviewCount = 4,
  criticalCount = 2,
  className,
}: TransactionHealthScoreProps) {
  // Determine score color
  const getScoreColor = (val: number) => {
    if (val >= 80) return "text-emerald-400 border-emerald-500/30";
    if (val >= 60) return "text-amber-400 border-amber-500/30";
    return "text-rose-400 border-rose-500/30";
  };

  const getScoreRating = (val: number) => {
    if (val >= 80) return "Moderate Risk Profile";
    if (val >= 60) return "Elevated Inconsistencies";
    return "High Risk Burden";
  };

  return (
    <Card className={cn("p-5 flex flex-col justify-between", className)}>
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider block">
            Transaction Health Index
          </span>
          <span className="text-xs text-zinc-500">
            Calculated across all uploaded bundle documents
          </span>
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded bg-surface-subtle border border-surface-border text-zinc-400 font-mono">
          Informational
        </span>
      </div>

      <div className="my-5 flex flex-col sm:flex-row items-center gap-6">
        {/* Score Ring / Pill */}
        <div className="flex flex-col items-center justify-center">
          <div
            className={cn(
              "w-24 h-24 rounded-full border-4 flex flex-col items-center justify-center bg-surface-subtle/50",
              getScoreColor(score)
            )}
          >
            <span className="text-3xl font-black tracking-tight font-mono">
              {score}
            </span>
            <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">
              / 100
            </span>
          </div>
          <span className="mt-2 text-xs font-medium text-zinc-300 text-center">
            {getScoreRating(score)}
          </span>
        </div>

        {/* Detailed clause breakdown */}
        <div className="flex-1 w-full space-y-2.5">
          <div className="flex items-center justify-between text-xs">
            <span className="text-zinc-400 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Standard / Balanced Clauses</span>
            </span>
            <span className="font-mono text-zinc-200 font-medium">
              {verifiedCount} ({Math.round((verifiedCount / totalClauses) * 100)}%)
            </span>
          </div>
          <div className="w-full bg-zinc-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-emerald-400 h-1.5 rounded-full"
              style={{ width: `${(verifiedCount / totalClauses) * 100}%` }}
            />
          </div>

          <div className="flex items-center justify-between text-xs">
            <span className="text-zinc-400 flex items-center gap-1.5">
              <HelpCircle className="w-3.5 h-3.5 text-amber-400" />
              <span>Review Required / Ambiguous</span>
            </span>
            <span className="font-mono text-zinc-200 font-medium">
              {reviewCount}
            </span>
          </div>

          <div className="flex items-center justify-between text-xs">
            <span className="text-zinc-400 flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
              <span>High Risk / Discrepancies</span>
            </span>
            <span className="font-mono text-rose-400 font-medium">
              {criticalCount}
            </span>
          </div>
        </div>
      </div>

      <div className="pt-3 border-t border-surface-border text-[11px] text-zinc-500">
        Score reflects parity between marketing materials, allotment terms, and the draft sale agreement.
      </div>
    </Card>
  );
}
