"use client";

import React from "react";
import { AlertTriangle, Clock, ArrowRight } from "lucide-react";

import { TimelineEvent } from "@/types/copilot";

interface TimelineConflictAlertProps {
  conflictingEventsCount: number;
  onExploreConflicts?: () => void;
  conflictSummary?: string;
  conflictingEvents?: TimelineEvent[];
}

export const TimelineConflictAlert: React.FC<TimelineConflictAlertProps> = ({
  conflictingEventsCount,
  onExploreConflicts,
  conflictSummary,
  conflictingEvents,
}) => {
  if (conflictingEventsCount === 0) return null;

  let alertText = conflictSummary;
  if (!alertText && conflictingEvents && conflictingEvents.length >= 2) {
    const [ev1, ev2] = conflictingEvents;
    const doc1 = ev1.documentName || "Preliminary document";
    const date1 = ev1.eventDate || "scheduled date";
    const doc2 = ev2.documentName || "formal agreement";
    const date2 = ev2.eventDate || "later deadline";
    alertText = `${doc1} specifies handover by ${date1}, whereas ${doc2} stipulates ${date2}.`;
  }
  if (!alertText) {
    alertText = `${conflictingEventsCount} critical handover timeline ${
      conflictingEventsCount === 1 ? "discrepancy" : "discrepancies"
    } detected across transaction documents.`;
  }

  return (
    <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/25 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg bg-amber-500/20 text-amber-300 shrink-0">
          <AlertTriangle className="w-5 h-5" />
        </div>
        <div>
          <h4 className="text-sm font-semibold text-amber-200">
            {conflictingEventsCount} Critical Handover Timeline {conflictingEventsCount === 1 ? "Discrepancy" : "Discrepancies"} Detected
          </h4>
          <p className="text-xs text-amber-300/80 mt-0.5 leading-relaxed">
            {alertText}
          </p>
        </div>
      </div>

      {onExploreConflicts && (
        <button
          onClick={onExploreConflicts}
          className="shrink-0 px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-200 border border-amber-500/30 font-medium text-xs transition-colors flex items-center gap-1.5 self-start sm:self-auto"
        >
          <span>Filter Conflicts</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
};
