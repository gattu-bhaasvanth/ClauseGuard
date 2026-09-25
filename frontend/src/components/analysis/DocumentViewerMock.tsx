"use client";

import React, { useState } from "react";
import {
  ZoomIn,
  ZoomOut,
  ChevronLeft,
  ChevronRight,
  Search,
  Maximize2,
  FileText,
  Bookmark,
  Eye,
} from "lucide-react";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/utils";

interface DocumentViewerMockProps {
  activeClauseId?: string;
  selectedClause?: any;
  documents?: Array<{ id: string; fileName?: string; file_name?: string; pageCount?: number }>;
  projectName?: string;
  unitNumber?: string;
  className?: string;
}

export function DocumentViewerMock({
  activeClauseId = "cls-01",
  selectedClause,
  documents = [],
  projectName,
  unitNumber,
  className,
}: DocumentViewerMockProps) {
  const isSkyView = !documents || documents.length === 0 || documents.some(d => (d.fileName || d.file_name || "").includes("SkyView"));
  
  const docList = documents && documents.length > 0
    ? documents.map(d => d.fileName || d.file_name || "Document.pdf")
    : [
        "Builder_Buyer_Agreement_SkyView_A1204.pdf",
        "Signed_Allotment_Letter.pdf",
        "SkyView_Official_Brochure.pdf",
        "Payment_Schedule_Milestone_Plan.pdf",
      ];

  const [currentPage, setCurrentPage] = useState<number>(selectedClause?.pageNumber || 1);
  const [zoomLevel, setZoomLevel] = useState(100);
  const [activeDoc, setActiveDoc] = useState(docList[0]);

  React.useEffect(() => {
    if (docList.length > 0 && !docList.includes(activeDoc)) {
      setActiveDoc(docList[0]);
    }
  }, [docList, activeDoc]);

  React.useEffect(() => {
    if (selectedClause?.pageNumber) {
      setCurrentPage(selectedClause.pageNumber);
    }
  }, [selectedClause]);

  const displayProject = projectName || (isSkyView ? "SkyView Residency" : "Real Estate Transaction");
  const displayUnit = unitNumber || (isSkyView ? "Unit No. A-1204, Tower A" : "Unit Record");

  return (
    <div className={cn("flex flex-col h-full bg-zinc-950 border border-surface-border rounded-xl overflow-hidden shadow-2xl", className)}>
      {/* Top Document Viewer Toolbar */}
      <div className="h-12 bg-surface border-b border-surface-border px-3 sm:px-4 flex items-center justify-between gap-2 text-xs flex-shrink-0">
        {/* Document Selector */}
        <div className="flex items-center gap-2 min-w-0">
          <FileText className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <select
            value={activeDoc}
            onChange={(e) => setActiveDoc(e.target.value)}
            className="bg-zinc-900 border border-zinc-700/80 rounded px-2 py-1 text-xs text-zinc-200 focus:outline-none focus:border-emerald-500 truncate max-w-[200px] sm:max-w-xs"
          >
            {docList.map((dName, idx) => (
              <option key={idx} value={dName}>
                {dName}
              </option>
            ))}
          </select>
        </div>

        {/* Page navigation & Zoom controls */}
        <div className="flex items-center gap-3">
          {/* Pagination */}
          <div className="flex items-center gap-1 bg-surface-subtle border border-surface-border rounded px-1.5 py-0.5">
            <button
              onClick={() => setCurrentPage((p: number) => Math.max(1, p - 1))}
              disabled={currentPage <= 1}
              className="p-1 text-zinc-400 hover:text-white disabled:opacity-30"
              aria-label="Previous Page"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <span className="font-mono text-[11px] text-zinc-300 px-1">
              Page {currentPage} of {isSkyView ? 38 : Math.max(currentPage, 5)}
            </span>
            <button
              onClick={() => setCurrentPage((p: number) => Math.min(isSkyView ? 38 : 50, p + 1))}
              disabled={currentPage >= (isSkyView ? 38 : 50)}
              className="p-1 text-zinc-400 hover:text-white disabled:opacity-30"
              aria-label="Next Page"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Zoom */}
          <div className="hidden sm:flex items-center gap-1 bg-surface-subtle border border-surface-border rounded px-1.5 py-0.5">
            <button
              onClick={() => setZoomLevel((z) => Math.max(75, z - 10))}
              className="p-1 text-zinc-400 hover:text-white"
              aria-label="Zoom out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="font-mono text-[11px] text-zinc-300 w-10 text-center">
              {zoomLevel}%
            </span>
            <button
              onClick={() => setZoomLevel((z) => Math.min(150, z + 10))}
              className="p-1 text-zinc-400 hover:text-white"
              aria-label="Zoom in"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Document Viewport / Canvas Simulation */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-8 flex justify-center bg-zinc-900/60 custom-scrollbar">
        <div
          className="w-full max-w-2xl bg-zinc-950 border border-zinc-800 rounded-sm shadow-2xl p-8 sm:p-12 text-zinc-300 font-serif leading-relaxed text-xs relative select-text"
          style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: "top center" }}
        >
          {/* Header Stamped Legal Deed Watermark */}
          <div className="border-b border-zinc-800 pb-4 mb-6 text-center font-sans">
            <div className="inline-block px-3 py-1 rounded bg-zinc-900 border border-zinc-800 text-[10px] text-zinc-500 uppercase tracking-widest font-mono">
              Certified Legal Record • Document Intelligence
            </div>
            <h2 className="text-sm font-bold text-zinc-200 mt-2 font-serif tracking-normal uppercase">
              {activeDoc.replace(/_/g, " ").replace(/\.pdf$/i, "")}
            </h2>
            <p className="text-[11px] text-zinc-500 font-sans mt-0.5">
              {displayUnit} • {displayProject}
            </p>
          </div>

          {/* Document Content with Interactive Highlight Boxes */}
          {!isSkyView && selectedClause ? (
            <div className="space-y-4 font-serif text-[11px] text-zinc-300 leading-normal">
              <div>
                <h4 className="font-bold text-zinc-200 font-sans text-xs mb-1 uppercase">
                  {selectedClause.category || "LEGAL PROVISION"}
                </h4>
                <div className="p-3.5 rounded bg-emerald-500/10 border-2 border-emerald-500 shadow-md ring-2 ring-emerald-500/20">
                  <span className="font-bold text-emerald-400 font-sans block mb-1">
                    {selectedClause.clauseNumber ? `${selectedClause.clauseNumber}: ` : ""}{selectedClause.title || "Selected Provision"}
                  </span>
                  <p className="leading-relaxed whitespace-pre-wrap">
                    &ldquo;{selectedClause.fullExcerpt || selectedClause.previewText || "Clause text excerpt"}&rdquo;
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-4 font-serif text-[11px] text-zinc-300 leading-normal">
              <div>
                <h4 className="font-bold text-zinc-200 font-sans text-xs mb-1">
                  ARTICLE IV: SPECIFICATIONS & MEASUREMENTS
                </h4>
                <div
                  className={cn(
                    "p-2.5 rounded transition-all",
                    activeClauseId === "cls-03"
                      ? "bg-purple-500/20 border-2 border-purple-500 shadow-md ring-2 ring-purple-500/20"
                      : "hover:bg-zinc-900/50"
                  )}
                >
                  <span className="font-bold text-purple-400 font-sans block mb-1">
                    Clause 4.1 (RERA Carpet Area & Variances):
                  </span>
                  <p>
                    &ldquo;The Allottee hereby agrees that the Apartment has a RERA Carpet Area of <strong>1,380 sq. ft. (128.20 sq. m.)</strong>. The Promoter reserves the right to make architectural adjustments resulting in up to <strong>&plusmn;3% variation</strong> in carpet area without alteration to the agreed Total Consideration.&rdquo;
                  </p>
                </div>
              </div>

              <div>
                <h4 className="font-bold text-zinc-200 font-sans text-xs mb-1">
                  ARTICLE V: PAYMENT TERMS & SCHEDULE
                </h4>
                <div
                  className={cn(
                    "p-2.5 rounded transition-all",
                    activeClauseId === "cls-02"
                      ? "bg-rose-500/20 border-2 border-rose-500 shadow-md ring-2 ring-rose-500/20"
                      : "hover:bg-zinc-900/50"
                  )}
                >
                  <span className="font-bold text-rose-400 font-sans block mb-1">
                    Clause 5.3 (Late Payment Default Rate):
                  </span>
                  <p>
                    &ldquo;Time is of the essence in this Agreement. If the Allottee fails to pay any installment on or before the due date, the Allottee shall be liable to pay interest on delayed payment at the rate of <strong>18% per annum compounded monthly</strong> from the due date until full realization of the outstanding installment.&rdquo;
                  </p>
                </div>
              </div>

              <div>
                <h4 className="font-bold text-zinc-200 font-sans text-xs mb-1">
                  ARTICLE VIII: POSSESSION & CONVEYANCE
                </h4>
                <div
                  className={cn(
                    "p-2.5 rounded transition-all",
                    activeClauseId === "cls-01"
                      ? "bg-rose-500/20 border-2 border-rose-500 shadow-md ring-2 ring-rose-500/20"
                      : "hover:bg-zinc-900/50"
                  )}
                >
                  <span className="font-bold text-rose-400 font-sans block mb-1">
                    Clause 8.2 (Developer Delay Compensation):
                  </span>
                  <p>
                    &ldquo;In the event of delay in offering possession of the Apartment beyond the agreed completion date and the <strong>grace period of 180 days</strong>, the Promoter shall pay compensation at the rate of <strong>Rs. 5/- (Rupees Five only) per sq. ft. of super area per month</strong> for the period of delay. Such compensation shall be adjusted against dues payable at possession.&rdquo;
                  </p>
                </div>
              </div>

              <div>
                <h4 className="font-bold text-zinc-200 font-sans text-xs mb-1">
                  ARTICLE XIV: CANCELLATION & LIQUIDATED DAMAGES
                </h4>
                <div
                  className={cn(
                    "p-2.5 rounded transition-all",
                    activeClauseId === "cls-04"
                      ? "bg-rose-500/20 border-2 border-rose-500 shadow-md ring-2 ring-rose-500/20"
                      : "hover:bg-zinc-900/50"
                  )}
                >
                  <span className="font-bold text-rose-400 font-sans block mb-1">
                    Clause 14.1 (Earnest Money Forfeiture):
                  </span>
                  <p>
                    &ldquo;In case of cancellation or termination of this Agreement by the Allottee for any reason whatsoever, the Promoter shall forfeit <strong>twenty percent (20%) of the Total Consideration</strong> along with brokerage charges as liquidated damages.&rdquo;
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Footer of the page */}
          <div className="border-t border-zinc-800/80 pt-6 mt-8 flex justify-between text-[10px] text-zinc-500 font-sans">
            <span>{displayProject} — {activeDoc}</span>
            <span>Page {currentPage} of {isSkyView ? 38 : Math.max(currentPage, 5)}</span>
          </div>
        </div>
      </div>

      {/* Bottom informational disclaimer bar */}
      <div className="h-8 bg-surface-subtle border-t border-surface-border px-4 flex items-center justify-between text-[10px] text-zinc-400">
        <span className="flex items-center gap-1.5">
          <Eye className="w-3 h-3 text-emerald-400" />
          <span>Interactive Document Viewer Mock</span>
        </span>
        <span className="font-mono text-zinc-500">{activeDoc}</span>
      </div>
    </div>
  );
}

