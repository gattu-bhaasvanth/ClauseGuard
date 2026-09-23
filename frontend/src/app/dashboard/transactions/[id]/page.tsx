"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  FileText,
  AlertTriangle,
  Split,
  Calendar,
  Layers,
  ArrowUpRight,
  Download,
  Share2,
  CheckCircle2,
  Eye,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { MOCK_SKYVIEW_TRANSACTION } from "@/mock/demoData";
import { PropertySummaryCard } from "@/components/transactions/PropertySummaryCard";
import { InconsistencyCard } from "@/components/transactions/InconsistencyCard";
import { RiskCard } from "@/components/transactions/RiskCard";
import { ObligationTimeline } from "@/components/transactions/ObligationTimeline";
import { DocumentTable } from "@/components/documents/DocumentTable";
import { TransactionHealthScore } from "@/components/dashboard/TransactionHealthScore";
import { SemanticExplorationWorkspace } from "@/components/transactions/SemanticExplorationWorkspace";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { SeverityBadge } from "@/components/shared/SeverityBadge";
import { LegalDisclaimerNotice } from "@/components/shared/LegalDisclaimerNotice";

export default function TransactionOverviewPage({
  params,
}: {
  params: { id: string };
}) {
  const transaction = MOCK_SKYVIEW_TRANSACTION;
  const [activeTab, setActiveTab] = useState<
    "inconsistencies" | "risks" | "timeline" | "documents" | "rag"
  >("inconsistencies");

  return (
    <div className="space-y-6">
      {/* Header with Project Title & Primary Action */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-surface-border">
        <div>
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-subtle border border-surface-border text-zinc-400">
              ID: {transaction.id}
            </span>
            <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 font-medium">
              <CheckCircle2 className="w-3 h-3 text-emerald-400" />
              Cross-Document Analysis Complete
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
            {transaction.title}
          </h1>
          <p className="text-xs text-zinc-400 mt-1">
            {transaction.property.location} • Promoter: {transaction.property.developer}
          </p>
        </div>

        <div className="flex items-center gap-2.5 flex-wrap">
          <Button
            variant={activeTab === "rag" ? "emerald" : "secondary"}
            size="sm"
            onClick={() => setActiveTab("rag")}
            className="gap-1.5 text-xs shadow-subtle-glow"
          >
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            <span>Ask ClauseGuard</span>
          </Button>
          <Link href={`/dashboard/transactions/${transaction.id}/analysis`}>
            <Button variant="emerald" size="sm" className="gap-1.5 text-xs shadow-subtle-glow">
              <Eye className="w-3.5 h-3.5" />
              <span>Split Document Viewer</span>
            </Button>
          </Link>
          <Button variant="secondary" size="sm" className="gap-1.5 text-xs">
            <Download className="w-3.5 h-3.5 text-zinc-400" />
            <span>Export Report</span>
          </Button>
        </div>
      </div>

      {/* Top Metrics Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <Card className="p-4">
          <span className="text-[10px] uppercase font-semibold text-zinc-400 tracking-wider block">
            Documents
          </span>
          <span className="text-2xl font-bold font-mono text-zinc-100 mt-1 block">
            {transaction.documentsCount}
          </span>
          <span className="text-[11px] text-zinc-500">Agreements & Brochure</span>
        </Card>

        <Card className="p-4 border-l-4 border-l-amber-500">
          <span className="text-[10px] uppercase font-semibold text-amber-400 tracking-wider block">
            Potential Issues
          </span>
          <span className="text-2xl font-bold font-mono text-amber-400 mt-1 block">
            {transaction.issuesCount}
          </span>
          <span className="text-[11px] text-zinc-500">2 Inconsistencies, 4 Risks</span>
        </Card>

        <Card className="p-4">
          <span className="text-[10px] uppercase font-semibold text-zinc-400 tracking-wider block">
            Important Dates
          </span>
          <span className="text-2xl font-bold font-mono text-zinc-100 mt-1 block">
            {transaction.importantDatesCount}
          </span>
          <span className="text-[11px] text-zinc-500">Delivery & Grace Window</span>
        </Card>

        <Card className="p-4">
          <span className="text-[10px] uppercase font-semibold text-zinc-400 tracking-wider block">
            Payment Obligations
          </span>
          <span className="text-2xl font-bold font-mono text-zinc-100 mt-1 block">
            {transaction.paymentObligationsCount}
          </span>
          <span className="text-[11px] text-zinc-500">Milestone Installments</span>
        </Card>
      </div>

      {/* Transaction Health + Property Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <TransactionHealthScore
          score={transaction.healthScore}
          totalClauses={24}
          verifiedCount={18}
          reviewCount={4}
          criticalCount={2}
          className="lg:col-span-1"
        />

        <PropertySummaryCard
          property={transaction.property}
          className="lg:col-span-2"
        />
      </div>

      {/* Structured Tabs for Inconsistencies, Risks, Dates, and Documents */}
      <div className="space-y-4">
        {/* Tab Headers */}
        <div className="flex items-center gap-2 border-b border-surface-border pb-1 overflow-x-auto">
          {[
            {
              id: "rag",
              label: "Ask ClauseGuard (RAG)",
              icon: Sparkles,
              highlight: true,
            },
            {
              id: "inconsistencies",
              label: `Potential Inconsistencies (${transaction.inconsistenciesCount})`,
              icon: Split,
              highlight: true,
            },
            {
              id: "risks",
              label: `Potential Risks (${transaction.risksCount})`,
              icon: AlertTriangle,
            },
            {
              id: "timeline",
              label: "Important Dates & Payments",
              icon: Calendar,
            },
            {
              id: "documents",
              label: `Documents (${transaction.documentsCount})`,
              icon: FileText,
            },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;

            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-medium transition-all whitespace-nowrap ${
                  isActive
                    ? "bg-zinc-800 text-white font-semibold border border-zinc-700/80 shadow-sm"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-surface-subtle"
                }`}
              >
                <Icon
                  className={`w-3.5 h-3.5 ${
                    isActive ? "text-emerald-400" : "text-zinc-500"
                  }`}
                />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab 1: Inconsistencies */}
        {activeTab === "inconsistencies" && (
          <div className="space-y-4">
            <div className="p-3.5 rounded-lg bg-surface-subtle border border-surface-border text-xs text-zinc-300 flex items-center justify-between">
              <div>
                <span className="font-semibold text-zinc-100 block">
                  Cross-Document Inconsistency Verification
                </span>
                <span className="text-[11px] text-zinc-400">
                  These discrepancies highlight where marketing claims or preliminary letters differ from formal draft contracts.
                </span>
              </div>
              <span className="text-[10px] text-purple-400 font-mono font-semibold">
                Side-by-Side Lineage
              </span>
            </div>

            <div className="space-y-4">
              {transaction.inconsistencies.map((inc) => (
                <InconsistencyCard
                  key={inc.id}
                  inconsistency={inc}
                  transactionId={transaction.id}
                />
              ))}
            </div>
          </div>
        )}

        {/* Tab 2: Potential Risks */}
        {activeTab === "risks" && (
          <div className="space-y-4">
            <div className="p-3.5 rounded-lg bg-surface-subtle border border-surface-border text-xs text-zinc-300">
              <span className="font-semibold text-zinc-100 block">
                Asymmetric Liability & High-Risk Clause Audit
              </span>
              <span className="text-[11px] text-zinc-400">
                Identifies contractual terms where legal or financial obligations are heavily weighted against the purchaser.
              </span>
            </div>

            <div className="space-y-4">
              {transaction.risks.map((risk) => (
                <RiskCard
                  key={risk.id}
                  risk={risk}
                  transactionId={transaction.id}
                />
              ))}
            </div>
          </div>
        )}

        {/* Tab 3: Timeline & Milestones */}
        {activeTab === "timeline" && (
          <ObligationTimeline
            dates={transaction.importantDates}
            payments={transaction.paymentObligations}
          />
        )}

        {/* Tab 4: Documents Table */}
        {activeTab === "documents" && (
          <DocumentTable
            documents={transaction.documents}
            transactionId={transaction.id}
          />
        )}

        {/* Tab 5: Semantic Exploration / RAG Workspace */}
        {activeTab === "rag" && (
          <SemanticExplorationWorkspace transactionId={transaction.id} />
        )}
      </div>

      <LegalDisclaimerNotice variant="banner" />
    </div>
  );
}
