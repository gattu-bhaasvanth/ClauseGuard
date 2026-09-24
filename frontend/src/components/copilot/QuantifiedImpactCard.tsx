"use client";

import React from "react";
import { AlertCircle, TrendingDown } from "lucide-react";

interface QuantifiedImpactCardProps {
  impactText: string;
}

export const QuantifiedImpactCard: React.FC<QuantifiedImpactCardProps> = ({
  impactText,
}) => {
  return (
    <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/25">
      <div className="flex items-center gap-2 mb-1.5 text-xs font-semibold text-rose-400 uppercase tracking-wider">
        <TrendingDown className="w-4 h-4 text-rose-400" />
        <span>Quantified Financial Harm / Exposure</span>
      </div>
      <p className="text-sm font-semibold text-rose-200 leading-snug">
        {impactText}
      </p>
    </div>
  );
};
