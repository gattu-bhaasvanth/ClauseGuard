"use client";

import React, { useState } from "react";
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

export default function DocumentAnalysisPage({
  params,
}: {
  params: { id: string };
}) {
  const transaction = MOCK_SKYVIEW_TRANSACTION;
  const clauses = transaction.clauses;
  const [selectedClause, setSelectedClause] = useState<ClauseItem>(clauses[0]);
  const [inspectingClause, setInspectingClause] = useState<ClauseItem | null>(null);
  const [isInspectorOpen, setIsInspectorOpen] = useState(false);

  const handleOpenInspector = (clause: ClauseItem) => {
    setInspectingClause(clause);
    setIsInspectorOpen(true);
  };

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
              {transaction.title} • {transaction.documents[0].fileName}
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
            activeClauseId={selectedClause.id}
            className="flex-1"
          />
        </div>

        {/* RIGHT PANE: Analysis Panel & Evidence Drawer (5 Columns on large screens) */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          {/* Top Half of Right Pane: Clause Findings List */}
          <div className="h-[360px] p-4 rounded-xl bg-surface border border-surface-border overflow-hidden flex flex-col">
            <ClauseList
              clauses={clauses}
              selectedClauseId={selectedClause.id}
              onSelectClause={(c) => setSelectedClause(c)}
              onInspectClause={handleOpenInspector}
            />
          </div>

          {/* Bottom Half of Right Pane: Selected Evidence Inspector */}
          <div className="flex-1">
            <EvidenceDrawer
              clause={selectedClause}
              documentName="Builder-Buyer Agreement"
              className="h-full"
              onInspectAI={() => handleOpenInspector(selectedClause)}
            />
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
