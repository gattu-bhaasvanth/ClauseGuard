"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  FileText,
  Shield,
  Layers,
  Sparkles,
  Info,
  Maximize2,
  Split,
} from "lucide-react";
import { MOCK_SKYVIEW_TRANSACTION } from "@/mock/demoData";
import { ClauseItem } from "@/types/transaction";
import { DocumentViewerMock } from "@/components/analysis/DocumentViewerMock";
import { ClauseList } from "@/components/analysis/ClauseList";
import { EvidenceDrawer } from "@/components/analysis/EvidenceDrawer";
import { ClassificationInspectorDrawer } from "@/components/intelligence/ClassificationInspectorDrawer";
import { Button } from "@/components/ui/Button";
import { SeverityBadge } from "@/components/shared/SeverityBadge";
import { LegalDisclaimerNotice } from "@/components/shared/LegalDisclaimerNotice";
import { fetchTransactionById } from "@/lib/api";

export default function DocumentAnalysisPage({
  params,
}: {
  params: { id: string };
}) {
  const transactionId = params.id || "skyview-a1204";
  const [transaction, setTransaction] = useState<any>(
    transactionId === "skyview-a1204" ? MOCK_SKYVIEW_TRANSACTION : null
  );

  useEffect(() => {
    if (transactionId === "skyview-a1204") {
      setTransaction(MOCK_SKYVIEW_TRANSACTION);
    } else {
      fetchTransactionById(transactionId)
        .then((res) => {
          if (res) {
            setTransaction(res);
            if (typeof window !== "undefined") {
              const proj = res.property?.project || res.property?.projectName || "";
              const unt = res.property?.unit || res.property?.unitNumber || "";
              const title = proj && unt ? `${proj} — ${unt}` : (res.title || "Custom Transaction");
              window.dispatchEvent(new CustomEvent("cg-tx-loaded", { detail: { id: res.id, title } }));
            }
          }
        })
        .catch(() => {});
    }
  }, [transactionId]);

  const clauses = transaction?.clauses || [];
  const [selectedClause, setSelectedClause] = useState<ClauseItem | null>(clauses[0] || null);
  const [inspectingClause, setInspectingClause] = useState<ClauseItem | null>(null);
  const [isInspectorOpen, setIsInspectorOpen] = useState(false);

  useEffect(() => {
    if (clauses.length > 0 && !selectedClause) {
      setSelectedClause(clauses[0]);
    }
  }, [clauses, selectedClause]);

  const handleOpenInspector = (clause: ClauseItem) => {
    setInspectingClause(clause);
    setIsInspectorOpen(true);
  };

  if (!transaction) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-3">
          <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs text-zinc-400">Loading analysis workspace...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Top Breadcrumb & Navigation Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-surface-border">
        <div className="flex items-center gap-3">
          <Link href={`/dashboard/transactions/${transaction.id}`}>
            <Button variant="ghost" size="sm" className="h-8 gap-1.5 text-zinc-400 hover:text-white">
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Overview</span>
            </Button>
          </Link>
          <div className="h-4 w-px bg-surface-border hidden sm:block" />
          <div>
            <h1 className="text-sm font-bold text-white flex items-center gap-2">
              <span>Document Analysis Workspace</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-subtle border border-surface-border text-emerald-400">
                Split-Pane View
              </span>
            </h1>
            <span className="text-[11px] text-zinc-400">
              {transaction.title} • {transaction.documents?.[0]?.fileName || "Document"}
            </span>
          </div>
        </div>

        {/* Demo Mode Notice */}
        <div className="flex items-center gap-2">
          <span className="text-[11px] text-zinc-400 hidden lg:inline">
            Interactive Mock: Clicking a clause highlights its text in the viewer
          </span>
          <SeverityBadge type="VERIFIED" label="Demo Shell" size="sm" />
        </div>
      </div>

      {/* SPLIT-PANE WORKSPACE: Left = Document Viewer, Right = Analysis & Evidence */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[750px]">
        {/* LEFT PANE: Document Viewer Placeholder (7 Columns on large screens) */}
        <div className="lg:col-span-7 h-[700px] lg:h-full flex flex-col">
          <DocumentViewerMock
            activeClauseId={selectedClause?.id || ""}
            selectedClause={selectedClause}
            documents={transaction.documents || []}
            projectName={transaction.property?.project || transaction.property?.projectName || transaction.title}
            unitNumber={transaction.property?.unit || transaction.property?.unitNumber}
            className="flex-1"
          />
        </div>

        {/* RIGHT PANE: Analysis Panel & Evidence Drawer (5 Columns on large screens) */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          {/* Top Half of Right Pane: Clause Findings List */}
          <div className="h-[360px] p-4 rounded-xl bg-surface border border-surface-border overflow-hidden flex flex-col">
            <ClauseList
              clauses={clauses}
              selectedClauseId={selectedClause?.id || ""}
              onSelectClause={(c) => setSelectedClause(c)}
              onInspectClause={handleOpenInspector}
            />
          </div>

          {/* Bottom Half of Right Pane: Selected Evidence Inspector */}
          <div className="flex-1">
            {selectedClause ? (
              <EvidenceDrawer
                clause={selectedClause}
                documentName={selectedClause.documentName || transaction.documents?.[0]?.fileName || "Document"}
                className="h-full"
                onInspectAI={() => handleOpenInspector(selectedClause)}
              />
            ) : (
              <div className="p-6 rounded-xl bg-surface border border-surface-border text-center text-xs text-zinc-400">
                Select a clause to inspect findings and evidence.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* AI Classification Inspector Slide-Over Panel */}
      <ClassificationInspectorDrawer
        clause={inspectingClause as any}
        isOpen={isInspectorOpen}
        onClose={() => setIsInspectorOpen(false)}
      />

      {/* Bottom informational disclaimer */}
      <LegalDisclaimerNotice variant="compact" />
    </div>
  );
}
