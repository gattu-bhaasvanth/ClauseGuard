"use client";

import React from "react";
import { BriefSection } from "@/types/copilot";
import { FileText, CheckCircle2 } from "lucide-react";

interface BriefSectionPreviewProps {
  section: BriefSection;
}

export const BriefSectionPreview: React.FC<BriefSectionPreviewProps> = ({
  section,
}) => {
  return (
    <div className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800 space-y-3">
      <div className="flex items-center gap-2 border-b border-zinc-800/80 pb-2">
        <span className="font-mono text-xs font-semibold text-emerald-400">
          Section {section.sectionNumber}
        </span>
        <h4 className="text-sm font-semibold text-zinc-100">
          {section.title}
        </h4>
      </div>

      <p className="text-xs text-zinc-300 leading-relaxed">
        {section.summary}
      </p>

      {section.bulletPoints && section.bulletPoints.length > 0 && (
        <div className="space-y-1.5 pt-1">
          {section.bulletPoints.map((bp, idx) => (
            <div key={idx} className="flex items-start gap-2 text-xs text-zinc-300">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
              <span>{bp}</span>
            </div>
          ))}
        </div>
      )}

      {section.evidenceLineage && section.evidenceLineage.length > 0 && (
        <div className="pt-2 border-t border-zinc-850">
          <span className="text-[10px] font-mono uppercase text-zinc-400 block mb-1">
            Evidence Lineage:
          </span>
          <div className="space-y-1">
            {section.evidenceLineage.map((ev, eIdx) => (
              <div
                key={eIdx}
                className="text-[11px] font-mono text-zinc-400 bg-zinc-950/60 px-2.5 py-1 rounded border border-zinc-850"
              >
                <span className="text-emerald-400/90">{ev.document}</span>
                {ev.clause && <span> • {ev.clause}</span>}
                <div className="text-zinc-400 truncate mt-0.5">&ldquo;{ev.excerpt}&rdquo;</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
