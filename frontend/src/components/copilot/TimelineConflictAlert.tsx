"use client";

import React from "react";
import { AlertTriangle, Clock, ArrowRight } from "lucide-react";

interface TimelineConflictAlertProps {
  conflictingEventsCount: number;
  onExploreConflicts?: () => void;
}

export const TimelineConflictAlert: React.FC<TimelineConflictAlertProps> = ({
  conflictingEventsCount,
  onExploreConflicts,
}) => {
  if (conflictingEventsCount === 0) return null;

  return (
    <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/25 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg bg-amber-500/20 text-amber-300 shrink-0">
          <AlertTriangle className="w-5 h-5" />
        </div>
        <div>
          <h4 className="text-sm font-semibold text-amber-200">
            {conflictingEventsCount} Critical Handover Timeline Discrepancies Detected
          </h4>
          <p className="text-xs text-amber-300/80 mt-0.5 leading-relaxed">
            Marketing Brochure promised delivery by <span className="font-semibold text-amber-200">31 Dec 2026</span>, whereas Builder-Buyer Agreement Clause 11.2 stipulates <span className="font-semibold text-amber-200">31 Dec 2027</span> plus an unconditional 180-day developer grace buffer (to June 2028).
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
