"use client";

import React from "react";
import { TimelineEvent, DateCertaintyType } from "@/types/copilot";
import { Calendar, AlertCircle, FileText, CheckCircle2, Clock, HelpCircle } from "lucide-react";

interface MilestoneCardProps {
  event: TimelineEvent;
  onInspectDocument?: (docName: string, pageNumber?: number) => void;
}

const CERTAINTY_STYLES: Record<DateCertaintyType, { label: string; badge: string }> = {
  CONTRACTUAL: {
    label: "Contractual",
    badge: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  },
  INFERRED: {
    label: "Inferred / Buffer",
    badge: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  },
  MARKETING: {
    label: "Marketing Claim",
    badge: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  },
  CONFLICTING: {
    label: "Conflicting",
    badge: "bg-amber-500/10 text-amber-400 border-amber-500/30",
  },
  UNCERTAIN: {
    label: "Conditional Milestone",
    badge: "bg-zinc-800 text-zinc-400 border-zinc-700",
  },
};

const STATUS_ICONS: Record<string, React.ReactNode> = {
  PAST: <CheckCircle2 className="w-4 h-4 text-emerald-400" />,
  UPCOMING: <Clock className="w-4 h-4 text-amber-400" />,
  TENTATIVE: <HelpCircle className="w-4 h-4 text-zinc-400" />,
};

export const MilestoneCard: React.FC<MilestoneCardProps> = ({
  event,
  onInspectDocument,
}) => {
  const certainty = CERTAINTY_STYLES[event.dateType] || CERTAINTY_STYLES.CONTRACTUAL;
  const statusIcon = STATUS_ICONS[event.status] || STATUS_ICONS.UPCOMING;

  return (
    <div
      className={`p-4 rounded-xl bg-[#111622] border transition-all duration-200 ease-out hover:-translate-y-0.5 hover:shadow-lg ${
        event.conflictingDate
          ? "border-amber-500/40 hover:border-amber-500/80 hover:shadow-amber-950/20"
          : "border-zinc-800 hover:border-zinc-700/90 hover:shadow-black/20"
      }`}
    >
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="mt-0.5">{statusIcon}</div>
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-1.5">
              <span
                className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded border ${certainty.badge}`}
              >
                {certainty.label}
              </span>
              <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-zinc-900 text-zinc-400 border border-zinc-800">
                {event.status}
              </span>
              {event.isDerived && (
                <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  Derived
                </span>
              )}
              {event.precision === "YEAR" && (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">
                  Year-Only
                </span>
              )}
              {event.clauseReference && (
                <span className="text-[10px] font-mono text-zinc-400 bg-zinc-900 px-2 py-0.5 rounded">
                  {event.clauseReference}
                </span>
              )}
            </div>

            <h4 className="text-sm font-semibold text-zinc-100">
              {event.title}
            </h4>

            <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
              {event.description}
            </p>
          </div>
        </div>

        {/* Date & Obligation Column */}
        <div className="shrink-0 flex sm:flex-col sm:items-end justify-between sm:justify-start gap-1">
          <div className="flex items-center gap-1.5 text-xs font-mono font-semibold text-zinc-200 bg-zinc-900/80 px-2.5 py-1 rounded border border-zinc-800">
            <Calendar className="w-3.5 h-3.5 text-emerald-400" />
            <span>{event.eventDate || "Milestone-Triggered"}</span>
          </div>

          {event.linkedObligationFormatted && (
            <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              Installment: {event.linkedObligationFormatted}
            </span>
          )}
        </div>
      </div>

      {/* Conflict Warning Box */}
      {event.conflictingDate && (
        <div className="mt-3 p-2.5 rounded-lg bg-amber-950/20 border border-amber-900/30 text-xs text-amber-300 flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-amber-200">Date Conflict: </span>
            <span>
              {event.conflictDetails || `Contradicts milestone date (${event.conflictingDate}) in transaction documents.`}
            </span>
          </div>
        </div>
      )}

      {/* Citation Tag */}
      {event.documentName && (
        <div className="mt-3 pt-2 border-t border-zinc-850 flex items-center justify-between text-[11px] text-zinc-400">
          <div className="flex items-center gap-1.5 truncate">
            <FileText className="w-3 h-3 text-zinc-400 shrink-0" />
            <span className="truncate">{event.documentName}</span>
            {event.pageNumber && <span>(Page {event.pageNumber})</span>}
          </div>
          {onInspectDocument && (
            <button
              onClick={() => onInspectDocument(event.documentName!, event.pageNumber)}
              className="text-emerald-400 hover:text-emerald-300 font-medium shrink-0 ml-2"
            >
              View Source →
            </button>
          )}
        </div>
      )}
    </div>
  );
};
