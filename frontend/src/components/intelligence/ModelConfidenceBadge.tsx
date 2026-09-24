"use client";

import React from "react";
import { Sparkles, Shield, AlertCircle, HelpCircle } from "lucide-react";

interface ModelConfidenceBadgeProps {
  confidence?: number;
  source?: string;
  onClick?: () => void;
  className?: string;
}

export function ModelConfidenceBadge({
  confidence = 1.0,
  source = "ML_TRANSFORMER",
  onClick,
  className = "",
}: ModelConfidenceBadgeProps) {
  const pct = Math.round(confidence * 100);
  const isML = source === "ML_TRANSFORMER";

  let badgeColor = "bg-emerald-500/10 text-emerald-300 border-emerald-500/30 hover:bg-emerald-500/20";
  let Icon = Sparkles;
  let label = `${pct}% Confident`;

  if (confidence < 0.65) {
    badgeColor = "bg-amber-500/10 text-amber-300 border-amber-500/30 hover:bg-amber-500/20";
    Icon = AlertCircle;
    label = `${pct}% • Review Needed`;
  } else if (confidence < 0.85) {
    badgeColor = "bg-zinc-800 text-zinc-300 border-zinc-700 hover:bg-zinc-750";
    Icon = Shield;
    label = `${pct}% Confident`;
  }

  return (
    <button
      type="button"
      data-testid="model-confidence-badge"
      onClick={onClick}
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full border text-[11px] font-medium transition-colors cursor-pointer select-none ${badgeColor} ${className}`}
      title={`Classification source: ${isML ? "Local ML Prototype Engine" : "Deterministic Heuristics"}. Click to inspect alternatives & evidence.`}
    >
      <Icon className="w-3 h-3 flex-shrink-0" />
      <span className="font-mono">{label}</span>
      <span className="text-[9px] uppercase px-1 rounded bg-black/30 font-semibold tracking-wider text-zinc-400">
        {isML ? "ML" : "Rule"}
      </span>
    </button>
  );
}
