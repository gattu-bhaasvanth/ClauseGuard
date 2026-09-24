"use client";

import React, { useState, useEffect } from "react";
import { ExplainableRiskData } from "@/types/copilot";
import { fetchExplainableRisk } from "@/lib/api";
import { QuantifiedImpactCard } from "./QuantifiedImpactCard";
import { NegotiationScriptBox } from "./NegotiationScriptBox";
import {
  X,
  Scale,
  FileText,
  AlertTriangle,
  Loader2,
  ExternalLink,
  ShieldAlert,
} from "lucide-react";

interface ExplainableRiskDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  bundleId: string;
  findingId: string | null;
  onOpenDocumentViewer?: (docName: string, pageNumber: number) => void;
}

export const ExplainableRiskDrawer: React.FC<ExplainableRiskDrawerProps> = ({
  isOpen,
  onClose,
  bundleId,
  findingId,
  onOpenDocumentViewer,
}) => {
  const [data, setData] = useState<ExplainableRiskData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen && findingId) {
      setIsLoading(true);
      fetchExplainableRisk(bundleId, findingId)
        .then((res) => setData(res))
        .catch(() => setData(null))
        .finally(() => setIsLoading(false));
    }
  }, [isOpen, findingId, bundleId]);

  // Global Escape key listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm transition-opacity duration-300"
      role="dialog"
      aria-modal="true"
      aria-label="Explainable Risk Intelligence"
    >
      <div className="w-full max-w-2xl bg-[#0b0e14] border-l border-zinc-800 h-full flex flex-col shadow-2xl animate-in slide-in-from-right duration-300">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-zinc-800 bg-[#10141d]">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-rose-500/10 border border-rose-500/20">
              <ShieldAlert className="w-5 h-5 text-rose-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20">
                  {data?.severity || "CRITICAL"}
                </span>
                <span className="text-xs font-mono text-zinc-400">
                  ID: {findingId}
                </span>
              </div>
              <h3 className="text-base font-semibold text-zinc-100 mt-0.5">
                {data?.title || "Explainable Risk Analysis"}
              </h3>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <kbd className="hidden sm:inline-block text-[10px] text-zinc-400 bg-zinc-800 px-2 py-1 rounded border border-zinc-700 font-mono">
              ESC
            </kbd>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors"
              aria-label="Close explainability drawer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-24 text-zinc-400">
              <Loader2 className="w-8 h-8 text-emerald-400 animate-spin mb-3" />
              <p className="text-sm">Synthesizing statutory benchmarks and evidence lineage...</p>
            </div>
          ) : data ? (
            <>
              {/* Question Banner */}
              <div className="p-3.5 rounded-xl bg-zinc-900/60 border border-zinc-800 flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-amber-300">
                    Why is this clause considered risky?
                  </h4>
                  <p className="text-xs text-zinc-300 mt-1 leading-relaxed">
                    {data.plainEnglishHarm}
                  </p>
                </div>
              </div>

              {/* Quantified Financial Impact */}
              {data.quantifiedImpact && (
                <QuantifiedImpactCard impactText={data.quantifiedImpact} />
              )}

              {/* Statutory Benchmark Section */}
              <div className="p-4 rounded-xl bg-[#121622] border border-zinc-800/90 space-y-2">
                <div className="flex items-center gap-2 text-xs font-semibold text-zinc-200 uppercase tracking-wide">
                  <Scale className="w-4 h-4 text-emerald-400" />
                  <span>Statutory Benchmark & Regulatory Rulings</span>
                </div>
                <p className="text-xs text-zinc-300 leading-relaxed">
                  {data.statutoryBenchmark}
                </p>
              </div>

              {/* 5-Tier Evidence Lineage */}
              <div className="p-4 rounded-xl bg-[#111622] border border-zinc-800 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-semibold text-zinc-200 uppercase tracking-wide">
                    <FileText className="w-4 h-4 text-emerald-400" />
                    <span>5-Tier Evidence Lineage</span>
                  </div>
                  {onOpenDocumentViewer && (
                    <button
                      onClick={() =>
                        onOpenDocumentViewer(
                          data.lineage.documentName,
                          data.lineage.pageNumber
                        )
                      }
                      className="text-xs text-emerald-400 hover:text-emerald-300 inline-flex items-center gap-1 font-medium transition-colors"
                    >
                      <span>Jump to Page {data.lineage.pageNumber}</span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                  <div className="p-2 rounded bg-zinc-900 border border-zinc-800">
                    <span className="text-zinc-400 text-[10px] block">Document:</span>
                    <span className="text-zinc-200 truncate block">
                      {data.lineage.documentName}
                    </span>
                  </div>
                  <div className="p-2 rounded bg-zinc-900 border border-zinc-800">
                    <span className="text-zinc-400 text-[10px] block">Page & Clause:</span>
                    <span className="text-emerald-400 block">
                      Page {data.lineage.pageNumber} • {data.lineage.clauseNumber || "General"}
                    </span>
                  </div>
                </div>

                {/* Verbatim Excerpt */}
                <div className="p-3.5 rounded-lg bg-zinc-950 border border-zinc-800 text-xs font-mono text-zinc-300 leading-relaxed border-l-2 border-l-emerald-500">
                  <span className="text-[10px] uppercase tracking-wider text-zinc-400 block mb-1">
                    Verbatim Operative Excerpt:
                  </span>
                  &ldquo;{data.lineage.verbatimExcerpt}&rdquo;
                </div>
              </div>

              {/* Actionable Negotiation Amendment Script */}
              {data.recommendedNegotiationScript && (
                <NegotiationScriptBox script={data.recommendedNegotiationScript} />
              )}
            </>
          ) : (
            <div className="text-center py-20 text-zinc-400 text-sm">
              Finding details could not be loaded.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
