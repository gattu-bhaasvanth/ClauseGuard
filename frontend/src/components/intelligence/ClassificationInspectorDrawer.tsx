"use client";

import React, { useEffect } from "react";
import { X, Sparkles, Shield, AlertTriangle, CheckCircle2, ChevronRight, Layers, FileText } from "lucide-react";
import { EnhancedClause } from "@/types/intelligence";
import { ModelConfidenceBadge } from "./ModelConfidenceBadge";

interface ClassificationInspectorDrawerProps {
  clause: EnhancedClause | null;
  isOpen: boolean;
  onClose: () => void;
  onReclassify?: (clauseId: string, newCategory: string) => void;
}

export function ClassificationInspectorDrawer({
  clause,
  isOpen,
  onClose,
  onReclassify,
}: ClassificationInspectorDrawerProps) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !clause) return null;

  const isML = clause.classificationSource === "ML_TRANSFORMER";
  const confidencePct = Math.round((clause.confidence ?? 1.0) * 100);

  return (
    <div
      data-testid="classification-inspector-drawer-backdrop"
      className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex justify-end transition-opacity duration-200"
      onClick={onClose}
    >
      <div
        data-testid="classification-inspector-drawer"
        className="w-full max-w-lg bg-surface border-l border-surface-border h-full overflow-y-auto shadow-2xl flex flex-col justify-between"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Drawer Header */}
        <div>
          <div className="p-5 border-b border-surface-border flex items-center justify-between sticky top-0 bg-surface/95 backdrop-blur z-10">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-surface-subtle border border-surface-border text-zinc-300">
                  {clause.clauseNumber}
                </span>
                <span className="text-xs text-zinc-500">Page {clause.pageNumber}</span>
              </div>
              <h2 className="text-base font-semibold text-white tracking-tight line-clamp-1">
                {clause.title}
              </h2>
            </div>
            <button
              type="button"
              data-testid="drawer-close-btn"
              onClick={onClose}
              className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-surface-subtle transition-colors"
              aria-label="Close drawer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-5 space-y-5">
            {/* Primary Classification Card */}
            <div className="rounded-xl border border-surface-border bg-surface-subtle/50 p-4 space-y-3">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <span className="text-[10px] uppercase font-semibold tracking-wider text-zinc-400">
                  Primary Classification
                </span>
                <ModelConfidenceBadge
                  confidence={clause.confidence}
                  source={clause.classificationSource}
                />
              </div>

              <div>
                <span className="text-lg font-bold text-white block">
                  {clause.category}
                </span>
                {clause.explanationNotes && (
                  <p className="text-xs text-zinc-300 mt-1 leading-relaxed">
                    {clause.explanationNotes}
                  </p>
                )}
              </div>

              {/* Confidence Calibration Bar */}
              <div className="space-y-1 pt-1">
                <div className="flex justify-between text-[11px] font-mono text-zinc-400">
                  <span>Calibrated Confidence</span>
                  <span className="text-emerald-400 font-semibold">{confidencePct}%</span>
                </div>
                <div className="w-full bg-zinc-800 h-2 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all duration-300 ${
                      confidencePct >= 85
                        ? "bg-emerald-500"
                        : confidencePct >= 65
                        ? "bg-zinc-400"
                        : "bg-amber-500"
                    }`}
                    style={{ width: `${confidencePct}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Top Alternatives (if available) */}
            {clause.topAlternatives && clause.topAlternatives.length > 0 && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-zinc-300 flex items-center gap-1.5">
                    <Layers className="w-3.5 h-3.5 text-zinc-400" />
                    Top Alternative Categories
                  </span>
                  <span className="text-[10px] text-zinc-500">Softmax distribution</span>
                </div>

                <div className="space-y-2">
                  {clause.topAlternatives.map((alt, i) => {
                    const altPct = Math.round(alt.probability * 100);
                    return (
                      <div
                        key={i}
                        className="rounded-lg border border-surface-border bg-surface-subtle/30 p-2.5 flex items-center justify-between gap-3 text-xs"
                      >
                        <div className="min-w-0 flex-1">
                          <span className="text-zinc-200 block truncate font-medium">
                            {alt.category}
                          </span>
                          <div className="w-full bg-zinc-800 h-1.5 rounded-full mt-1.5 overflow-hidden">
                            <div
                              className="h-full bg-zinc-500 rounded-full"
                              style={{ width: `${Math.max(4, altPct)}%` }}
                            />
                          </div>
                        </div>
                        <span className="font-mono text-zinc-400 text-[11px] font-semibold flex-shrink-0">
                          {altPct}%
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Statutory Risk Assessment (Deterministic Phase 4) */}
            <div className="space-y-2">
              <span className="text-xs font-semibold text-zinc-300 flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5 text-zinc-400" />
                Statutory Risk Assessment
              </span>
              <div className="rounded-xl border border-surface-border bg-surface-subtle/30 p-3.5 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-zinc-400">Risk Profile:</span>
                  <span
                    className={`text-xs px-2 py-0.5 rounded font-semibold uppercase ${
                      clause.status === "RISK"
                        ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                        : clause.status === "INCONSISTENCY"
                        ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                        : clause.status === "REVIEW_REQUIRED"
                        ? "bg-amber-500/10 text-amber-300 border border-amber-500/20"
                        : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                    }`}
                  >
                    {clause.status} {clause.severity && `• ${clause.severity}`}
                  </span>
                </div>
                <p className="text-xs text-zinc-300 leading-relaxed">
                  {clause.analysisSummary || "Standard contractual provision under regulatory benchmarks."}
                </p>
                {clause.riskDetails && (
                  <p className="text-xs text-amber-400/90 pt-1 border-t border-surface-border/50">
                    ⚠ {clause.riskDetails}
                  </p>
                )}
              </div>
            </div>

            {/* Verbatim Source Evidence */}
            <div className="space-y-2">
              <span className="text-xs font-semibold text-zinc-300 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-zinc-400" />
                Raw Legal Excerpt
              </span>
              <div className="rounded-xl border border-surface-border bg-surface-subtle/30 p-3 text-xs text-zinc-300 font-mono leading-relaxed max-h-48 overflow-y-auto whitespace-pre-wrap select-text">
                {clause.fullExcerpt || clause.previewText}
              </div>
            </div>
          </div>
        </div>

        {/* Audit Provenance Footer */}
        <div className="p-4 border-t border-surface-border bg-surface-subtle/80 text-[11px] text-zinc-400 space-y-1">
          <div className="flex items-center justify-between">
            <span>Model Version:</span>
            <span className="font-mono text-zinc-300">{clause.modelVersion || "cg-intel-v1.0.0"}</span>
          </div>
          <div className="flex items-center justify-between">
            <span>Dataset Provenance:</span>
            <span className="font-mono text-zinc-300">{clause.datasetVersion || "cg-statutory-corpus-v1.0"}</span>
          </div>
          <div className="flex items-center justify-between">
            <span>Engine:</span>
            <span className="font-mono text-emerald-400">
              {isML ? "Local ML Prototype (FastEmbed ONNX)" : "Phase 4 Deterministic Heuristic"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
