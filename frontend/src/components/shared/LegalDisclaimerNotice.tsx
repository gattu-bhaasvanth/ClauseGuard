import React from "react";
import { ShieldAlert } from "lucide-react";
import { cn } from "@/lib/utils";

interface LegalDisclaimerNoticeProps {
  className?: string;
  variant?: "banner" | "compact" | "footer";
}

export function LegalDisclaimerNotice({
  className,
  variant = "compact",
}: LegalDisclaimerNoticeProps) {
  if (variant === "footer") {
    return (
      <div className={cn("text-[11px] text-zinc-500 leading-relaxed border-t border-surface-border pt-4", className)}>
        <p>
          <strong className="text-zinc-400">Informational Document Analysis Notice:</strong> ClauseGuard is an automated document intelligence system designed to help users identify potential risks and cross-document inconsistencies. ClauseGuard does not provide legal advice, representation, or formal opinions. All outputs require independent professional verification before executing binding agreements.
        </p>
      </div>
    );
  }

  if (variant === "banner") {
    return (
      <div
        className={cn(
          "flex items-start gap-3 p-4 rounded-xl border border-zinc-800 bg-surface/70 text-xs text-zinc-400 leading-relaxed",
          className
        )}
      >
        <ShieldAlert className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-zinc-200 block mb-0.5">
            Informational Document Analysis System
          </span>
          <p>
            ClauseGuard provides automated discrepancy detection and clause risk tagging. It is not an attorney and does not offer legal advice. Findings marked as &ldquo;Potential Risk&rdquo; or &ldquo;Potential Inconsistency&rdquo; are informational indicators that require verification by qualified legal counsel.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex items-center gap-2 px-3 py-1.5 rounded-lg border border-zinc-800/80 bg-surface-subtle/50 text-[11px] text-zinc-400",
        className
      )}
    >
      <ShieldAlert className="w-3.5 h-3.5 text-zinc-400 flex-shrink-0" />
      <span>
        Informational analysis only. Not legal advice. Requires professional verification.
      </span>
    </div>
  );
}
