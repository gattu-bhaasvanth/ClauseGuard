import React from "react";
import {
  AlertTriangle,
  AlertOctagon,
  AlertCircle,
  Info,
  GitCompare,
  CheckCircle2,
  FileQuestion,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { SeverityLevel, FindingType } from "@/types/transaction";

export type BadgeTone =
  | SeverityLevel
  | FindingType
  | "POTENTIAL_INCONSISTENCY"
  | "REVIEW_REQUIRED";

interface SeverityBadgeProps {
  type: BadgeTone;
  label?: string;
  size?: "sm" | "md";
  className?: string;
  showIcon?: boolean;
}

export function SeverityBadge({
  type,
  label,
  size = "md",
  className,
  showIcon = true,
}: SeverityBadgeProps) {
  let displayLabel = label;
  let icon = <Info className="w-3.5 h-3.5" />;
  let colorStyles = "bg-zinc-800 text-zinc-300 border-zinc-700/60";

  switch (type) {
    case "CRITICAL":
      displayLabel = label || "Critical Risk";
      icon = <AlertOctagon className="w-3.5 h-3.5 text-rose-400" />;
      colorStyles = "bg-rose-500/10 text-rose-300 border-rose-500/30";
      break;

    case "HIGH":
      displayLabel = label || "High Risk";
      icon = <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />;
      colorStyles = "bg-rose-500/10 text-rose-300 border-rose-500/30";
      break;

    case "MEDIUM":
    case "REVIEW_REQUIRED":
      displayLabel = label || (type === "REVIEW_REQUIRED" ? "Review Required" : "Medium Risk");
      icon = <AlertCircle className="w-3.5 h-3.5 text-amber-400" />;
      colorStyles = "bg-amber-500/10 text-amber-300 border-amber-500/30";
      break;

    case "LOW":
      displayLabel = label || "Low Risk";
      icon = <Info className="w-3.5 h-3.5 text-blue-400" />;
      colorStyles = "bg-blue-500/10 text-blue-300 border-blue-500/30";
      break;

    case "INCONSISTENCY":
    case "POTENTIAL_INCONSISTENCY":
      displayLabel = label || "Potential Inconsistency";
      icon = <GitCompare className="w-3.5 h-3.5 text-purple-400" />;
      colorStyles = "bg-purple-500/10 text-purple-300 border-purple-500/30";
      break;

    case "VERIFIED":
      displayLabel = label || "Verified / Balanced";
      icon = <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />;
      colorStyles = "bg-emerald-500/10 text-emerald-300 border-emerald-500/30";
      break;

    case "INFORMATION":
      displayLabel = label || "Information";
      icon = <FileQuestion className="w-3.5 h-3.5 text-zinc-400" />;
      colorStyles = "bg-zinc-800 text-zinc-300 border-zinc-700/60";
      break;

    default:
      displayLabel = label || type;
      break;
  }

  const sizeClasses =
    size === "sm"
      ? "text-[11px] px-2 py-0.5 gap-1.5"
      : "text-xs px-2.5 py-1 gap-1.5";

  return (
    <span
      className={cn(
        "inline-flex items-center font-medium rounded-md border tracking-tight transition-colors",
        sizeClasses,
        colorStyles,
        className
      )}
    >
      {showIcon && <span className="flex-shrink-0">{icon}</span>}
      <span>{displayLabel}</span>
    </span>
  );
}
