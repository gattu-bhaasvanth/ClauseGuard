"use client";

import React from "react";
import { BarChart3, AlertTriangle, Split, ShieldCheck, TrendingUp } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { SeverityBadge } from "@/components/shared/SeverityBadge";

export default function InsightsPage() {
  return (
    <div className="space-y-6">
      <div className="pb-4 border-b border-surface-border">
        <h1 className="text-2xl font-bold tracking-tight text-white">
          Portfolio Risk Insights
        </h1>
        <p className="text-xs text-zinc-400 mt-1">
          Aggregated clause patterns and recurring discrepancy trends across reviewed contracts
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-5">
          <div className="flex items-center gap-2 mb-3 text-rose-400">
            <AlertTriangle className="w-4 h-4" />
            <h3 className="text-sm font-semibold text-zinc-100">
              Most Prevalent Risk Clause
            </h3>
          </div>
          <span className="text-xl font-bold text-white block">
            Asymmetrical Delay Penalties
          </span>
          <p className="text-xs text-zinc-400 mt-2 leading-relaxed">
            Detected in 100% of reviewed Builder-Buyer Agreements. Average buyer default rate is 18% p.a., while developer delay compensation averages ~2.5% p.a.
          </p>
        </Card>

        <Card className="p-5">
          <div className="flex items-center gap-2 mb-3 text-purple-400">
            <Split className="w-4 h-4" />
            <h3 className="text-sm font-semibold text-zinc-100">
              Area Variance Frequency
            </h3>
          </div>
          <span className="text-xl font-bold text-white block">
            67% of Bundles
          </span>
          <p className="text-xs text-zinc-400 mt-2 leading-relaxed">
            Marketing brochures routinely advertise carpet area with integrated balconies, whereas sale agreements carve out balcony areas into separate sub-schedules.
          </p>
        </Card>

        <Card className="p-5">
          <div className="flex items-center gap-2 mb-3 text-emerald-400">
            <ShieldCheck className="w-4 h-4" />
            <h3 className="text-sm font-semibold text-zinc-100">
              Statutory Alignment
            </h3>
          </div>
          <span className="text-xl font-bold text-white block">
            RERA Mandates
          </span>
          <p className="text-xs text-zinc-400 mt-2 leading-relaxed">
            All 3 reviewed transactions contain valid state regulatory authority registration numbers and valid completion validity windows.
          </p>
        </Card>
      </div>
    </div>
  );
}
