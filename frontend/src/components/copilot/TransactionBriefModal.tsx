"use client";

import React, { useState, useEffect } from "react";
import { TransactionBriefData } from "@/types/copilot";
import { fetchTransactionBrief, downloadTransactionBriefPdf } from "@/lib/api";
import { BriefSectionPreview } from "./BriefSectionPreview";
import { X, Download, Printer, FileText, Loader2, ShieldCheck } from "lucide-react";

interface TransactionBriefModalProps {
  isOpen: boolean;
  onClose: () => void;
  bundleId: string;
}

export const TransactionBriefModal: React.FC<TransactionBriefModalProps> = ({
  isOpen,
  onClose,
  bundleId,
}) => {
  const [brief, setBrief] = useState<TransactionBriefData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setIsLoading(true);
      fetchTransactionBrief(bundleId)
        .then((res) => setBrief(res))
        .catch(() => setBrief(null))
        .finally(() => setIsLoading(false));
    }
  }, [isOpen, bundleId]);

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

  const handleDownloadPdf = async () => {
    try {
      setIsDownloading(true);
      const blob = await downloadTransactionBriefPdf(bundleId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ClauseGuard_Brief_${bundleId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error("PDF download failed:", err);
    } finally {
      setIsDownloading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-label="Executive Transaction Brief"
    >
      <div className="w-full max-w-4xl bg-[#0c1017] border border-zinc-800 rounded-2xl max-h-[90vh] flex flex-col shadow-2xl animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-zinc-800 bg-[#10141d] rounded-t-2xl">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-blue-500/10 border border-blue-500/20">
              <FileText className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-semibold text-zinc-100">
                  Executive Transaction Brief
                </h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  7 Evidence-Backed Sections
                </span>
              </div>
              <p className="text-xs text-zinc-400">
                {brief?.project || "Property Transaction"} ({brief?.unit}) • Generated: {brief?.generatedAt}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handlePrint}
              className="p-2 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors"
              title="Print Brief"
              aria-label="Print Brief"
            >
              <Printer className="w-4 h-4" />
            </button>
            <button
              onClick={handleDownloadPdf}
              disabled={isDownloading || !brief}
              className="px-3.5 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-zinc-950 font-semibold text-xs flex items-center gap-1.5 transition-all disabled:opacity-50"
            >
              {isDownloading ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Download className="w-3.5 h-3.5" />
              )}
              <span>Export PDF</span>
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors ml-1"
              aria-label="Close brief modal"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-24 text-zinc-400">
              <Loader2 className="w-8 h-8 text-emerald-400 animate-spin mb-3" />
              <p className="text-sm">Synthesizing 7 executive transaction sections...</p>
            </div>
          ) : brief ? (
            <>
              {/* Executive Snapshot Card */}
              <div className="p-4 rounded-xl bg-gradient-to-r from-[#121622] to-[#10141d] border border-zinc-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <span className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider block">
                    Forensic Overview
                  </span>
                  <h2 className="text-lg font-bold text-zinc-100">
                    {brief.project} — {brief.unit}
                  </h2>
                  <p className="text-xs text-zinc-400">
                    Developer: {brief.developer}
                  </p>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <span className="text-[10px] text-zinc-400 block font-mono">Total Capital At Risk:</span>
                    <span className="text-base font-bold font-mono text-rose-300">
                      {brief.totalFinancialExposure}
                    </span>
                  </div>
                  <div className="px-3.5 py-2 rounded-xl bg-zinc-900 border border-zinc-800 text-center">
                    <span className="text-[10px] text-zinc-400 block">Health Index</span>
                    <span className="text-lg font-bold font-mono text-emerald-400">
                      {brief.healthScore}/100
                    </span>
                  </div>
                </div>
              </div>

              {/* 7 Sections */}
              <div className="space-y-4">
                {brief.sections.map((sec) => (
                  <BriefSectionPreview key={sec.sectionNumber} section={sec} />
                ))}
              </div>

              {/* Disclaimer */}
              <div className="p-3.5 rounded-lg bg-zinc-900/40 border border-zinc-800/80 text-[11px] text-zinc-400 leading-relaxed flex items-start gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>{brief.disclaimer}</span>
              </div>
            </>
          ) : (
            <div className="text-center py-20 text-zinc-400 text-sm">
              Failed to generate brief.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
