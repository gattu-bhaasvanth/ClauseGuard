"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  X,
  FileText,
  ExternalLink,
  Copy,
  Check,
  ShieldCheck,
  Scale,
  Sparkles,
} from "lucide-react";
import { RAGCitation } from "@/types/rag";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";

interface SourceEvidenceModalProps {
  citation: RAGCitation | null;
  isOpen: boolean;
  onClose: () => void;
  transactionId: string;
}

export function SourceEvidenceModal({
  citation,
  isOpen,
  onClose,
  transactionId,
}: SourceEvidenceModalProps) {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !citation) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(citation.excerpt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const relevancePct = Math.round(citation.relevanceScore * 100);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-2xl rounded-xl border border-surface-border bg-surface-card p-6 shadow-2xl space-y-5 animate-in zoom-in-95 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between gap-4 border-b border-surface-border pb-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2 flex-wrap">
              <Badge variant="emerald" className="text-[11px] gap-1">
                <ShieldCheck className="w-3 h-3" />
                Grounded Source Citation
              </Badge>
              <Badge variant="purple" className="text-[11px]">
                {citation.documentType.replace(/_/g, " ")}
              </Badge>
              <Badge variant="blue" className="text-[11px]">
                Page {citation.pageNumber}
              </Badge>
              <span className="text-[11px] font-mono text-zinc-400">
                Relevance: {relevancePct}%
              </span>
            </div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2 mt-2">
              <FileText className="w-4 h-4 text-emerald-400" />
              {citation.documentName}
            </h3>
            {citation.clauseNumber && (
              <p className="text-xs text-emerald-400 font-medium font-mono">
                {citation.clauseNumber}
                {citation.clauseTitle ? `: ${citation.clauseTitle}` : ""}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Verbatim Excerpt */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-zinc-400">
            <span className="font-semibold uppercase tracking-wider text-[10px] text-zinc-400">
              Verbatim Contractual Excerpt
            </span>
            <button
              onClick={handleCopy}
              className="inline-flex items-center gap-1 text-[11px] text-zinc-400 hover:text-emerald-400 transition-colors"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400">Copied to clipboard</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy excerpt</span>
                </>
              )}
            </button>
          </div>
          <div className="p-4 rounded-lg bg-surface-base border border-surface-border text-xs leading-relaxed text-zinc-200 font-mono whitespace-pre-wrap select-all max-h-60 overflow-y-auto">
            {citation.excerpt}
          </div>
        </div>

        {/* Provenance Lineage Details */}
        <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border flex items-center justify-between text-xs">
          <div className="space-y-0.5">
            <span className="text-zinc-300 font-semibold block">
              Verified Legal Lineage
            </span>
            <span className="text-[11px] text-zinc-400">
              Document: {citation.documentName} → Page {citation.pageNumber} → {citation.clauseNumber || "Clause"}
            </span>
          </div>
          <div className="text-right">
            <span className="text-[10px] uppercase tracking-wider text-zinc-500 block">
              Retrieval Model
            </span>
            <span className="text-[11px] font-mono text-emerald-400 font-semibold">
              FastEmbed 384-d
            </span>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between gap-3 pt-2">
          <p className="text-[11px] text-zinc-500">
            Informational verification only. Does not constitute legal advice.
          </p>
          <div className="flex items-center gap-2">
            <Link href={`/dashboard/transactions/${transactionId}/analysis`}>
              <Button variant="emerald" size="sm" className="gap-1.5 text-xs">
                <ExternalLink className="w-3.5 h-3.5" />
                <span>Open in Split Viewer</span>
              </Button>
            </Link>
            <Button variant="secondary" size="sm" onClick={onClose} className="text-xs">
              Close
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
