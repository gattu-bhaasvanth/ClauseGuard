"use client";

import React from "react";
import Link from "next/link";
import {
  Layers,
  FileText,
  AlertTriangle,
  CalendarCheck,
  Plus,
  ArrowRight,
  ShieldCheck,
  Split,
  Eye,
} from "lucide-react";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { RecentTransactionsTable } from "@/components/dashboard/RecentTransactionsTable";
import { TransactionHealthScore } from "@/components/dashboard/TransactionHealthScore";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { SeverityBadge } from "@/components/shared/SeverityBadge";
import { MOCK_ALL_TRANSACTIONS, MOCK_SKYVIEW_TRANSACTION } from "@/mock/demoData";

export default function DashboardOverviewPage() {
  const transactions = MOCK_ALL_TRANSACTIONS;
  const activeCount = transactions.length;
  const totalDocs = transactions.reduce((acc, t) => acc + t.documentsCount, 0);
  const totalIssues = transactions.reduce((acc, t) => acc + t.issuesCount, 0);
  const totalObligations = transactions.reduce(
    (acc, t) => acc + t.paymentObligationsCount,
    0
  );

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-surface-border">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white">
            Your Property Transactions
          </h1>
          <p className="text-xs text-zinc-400 mt-1">
            Real-estate transaction bundles and cross-document intelligence reports
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link href="/dashboard/transactions/skyview-a1204">
            <Button variant="secondary" size="sm" className="gap-1.5 text-xs">
              <Eye className="w-3.5 h-3.5 text-emerald-400" />
              <span>Demo: SkyView A-1204</span>
            </Button>
          </Link>
          <Link href="/dashboard/transactions/new">
            <Button variant="emerald" size="sm" className="gap-1.5 text-xs">
              <Plus className="w-3.5 h-3.5" />
              <span>Start New Transaction</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Summary Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Active Transactions"
          value={activeCount}
          subtitle="3 under active contract review"
          icon={Layers}
          badgeText="Active"
          badgeType="emerald"
        />
        <MetricCard
          title="Documents Analyzed"
          value={totalDocs}
          subtitle="Agreements, letters, and brochures"
          icon={FileText}
          badgeText="Indexed"
          badgeType="neutral"
        />
        <MetricCard
          title="Potential Issues"
          value={totalIssues}
          subtitle="Inconsistencies & risk clauses"
          icon={AlertTriangle}
          badgeText="Requires Review"
          badgeType="amber"
        />
        <MetricCard
          title="Upcoming Obligations"
          value={totalObligations}
          subtitle="Payment & construction milestones"
          icon={CalendarCheck}
          badgeText="Scheduled"
          badgeType="neutral"
        />
      </div>

      {/* Featured Active Transaction Spotlight & Health Meter */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Health Score Overview */}
        <TransactionHealthScore
          score={MOCK_SKYVIEW_TRANSACTION.healthScore}
          totalClauses={24}
          verifiedCount={18}
          reviewCount={4}
          criticalCount={2}
          className="lg:col-span-1"
        />

        {/* Featured Discrepancy Card */}
        <Card className="lg:col-span-2 p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <SeverityBadge type="POTENTIAL_INCONSISTENCY" />
                <span className="text-xs font-semibold text-zinc-200">
                  Top Priority Discrepancy (SkyView Flat A-1204)
                </span>
              </div>
              <span className="text-[10px] text-zinc-500 font-mono">
                Detected Across 2 Documents
              </span>
            </div>

            <h3 className="text-sm font-semibold text-zinc-100 mb-1">
              70 sq.ft Carpet Area Reduction Between Marketing & Contract
            </h3>
            <p className="text-xs text-zinc-400 mb-4 leading-relaxed">
              The project brochure guarantees 1,450 sq.ft carpet area, while Clause 4.1 of the Builder-Buyer Agreement defines binding RERA carpet area as 1,380 sq.ft with an added unilateral &plusmn;3% modification allowance.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border">
                <span className="text-[10px] text-zinc-400 font-semibold uppercase block mb-1">
                  Brochure (Page 4)
                </span>
                <p className="italic text-zinc-300 text-[11px]">
                  &ldquo;1450 sq.ft (134.7 sq.m) elite 3BHK carpet area with sundeck.&rdquo;
                </p>
              </div>

              <div className="p-3 rounded-lg bg-purple-950/20 border border-purple-500/30">
                <span className="text-[10px] text-purple-400 font-semibold uppercase block mb-1">
                  Agreement (Page 12, Clause 4.1)
                </span>
                <p className="italic text-purple-200 text-[11px]">
                  &ldquo;Carpet Area of 1,380 sq. ft. ... Promoter reserves right to make up to &plusmn;3% variation.&rdquo;
                </p>
              </div>
            </div>
          </div>

          <div className="pt-4 mt-4 border-t border-surface-border flex items-center justify-between">
            <span className="text-xs text-zinc-500">
              Potential financial impact: ~₹7.2 Lakhs in missing square footage.
            </span>
            <Link href="/dashboard/transactions/skyview-a1204">
              <Button variant="secondary" size="sm" className="gap-1.5 text-xs">
                <span>Inspect Transaction Details</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Button>
            </Link>
          </div>
        </Card>
      </div>

      {/* Recent Transactions Table */}
      <RecentTransactionsTable transactions={transactions} />
    </div>
  );
}
