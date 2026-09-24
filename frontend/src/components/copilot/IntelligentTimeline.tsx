"use client";

import React, { useState } from "react";
import { TimelineData, DateCertaintyType } from "@/types/copilot";
import { MilestoneCard } from "./MilestoneCard";
import { TimelineConflictAlert } from "./TimelineConflictAlert";
import { Calendar, Filter, Clock } from "lucide-react";

interface IntelligentTimelineProps {
  timelineData: TimelineData;
  onInspectDocument?: (docName: string, pageNumber?: number) => void;
}

export const IntelligentTimeline: React.FC<IntelligentTimelineProps> = ({
  timelineData,
  onInspectDocument,
}) => {
  const [filter, setFilter] = useState<"ALL" | "CONTRACTUAL" | "CONFLICTS" | "UNCERTAIN">("ALL");

  const filteredEvents = timelineData.events.filter((ev) => {
    if (filter === "CONTRACTUAL") return ev.dateType === "CONTRACTUAL";
    if (filter === "CONFLICTS") return Boolean(ev.conflictingDate);
    if (filter === "UNCERTAIN") return ev.dateType === "UNCERTAIN";
    return true;
  });

  return (
    <div className="space-y-5">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-[#111622] border border-zinc-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Clock className="w-5 h-5 text-amber-400" />
            <h3 className="text-base font-semibold text-zinc-100">
              Reconciled Transaction Timeline & Obligation Track
            </h3>
          </div>
          <p className="text-xs text-zinc-400">
            Harmonized chronological sequence of contractual dates, marketing promises, and construction-linked payment calls
          </p>
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-1.5 self-start sm:self-auto">
          <button
            onClick={() => setFilter("ALL")}
            className={`text-xs px-3 py-1.5 rounded-lg border transition-all ${
              filter === "ALL"
                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30 font-medium"
                : "bg-zinc-900 text-zinc-400 border-zinc-800 hover:text-zinc-200"
            }`}
          >
            All ({timelineData.totalEvents})
          </button>
          <button
            onClick={() => setFilter("CONTRACTUAL")}
            className={`text-xs px-3 py-1.5 rounded-lg border transition-all ${
              filter === "CONTRACTUAL"
                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30 font-medium"
                : "bg-zinc-900 text-zinc-400 border-zinc-800 hover:text-zinc-200"
            }`}
          >
            Contractual ({timelineData.contractualEventsCount})
          </button>
          <button
            onClick={() => setFilter("CONFLICTS")}
            className={`text-xs px-3 py-1.5 rounded-lg border transition-all ${
              filter === "CONFLICTS"
                ? "bg-amber-500/10 text-amber-400 border-amber-500/30 font-medium"
                : "bg-zinc-900 text-zinc-400 border-zinc-800 hover:text-zinc-200"
            }`}
          >
            Conflicts ({timelineData.conflictingEventsCount})
          </button>
          <button
            onClick={() => setFilter("UNCERTAIN")}
            className={`text-xs px-3 py-1.5 rounded-lg border transition-all ${
              filter === "UNCERTAIN"
                ? "bg-blue-500/10 text-blue-400 border-blue-500/30 font-medium"
                : "bg-zinc-900 text-zinc-400 border-zinc-800 hover:text-zinc-200"
            }`}
          >
            Milestone Calls ({timelineData.uncertainEventsCount})
          </button>
        </div>
      </div>

      {/* Conflict Alert Banner */}
      <TimelineConflictAlert
        conflictingEventsCount={timelineData.conflictingEventsCount}
        onExploreConflicts={() => setFilter("CONFLICTS")}
      />

      {/* Events List */}
      <div className="space-y-3">
        {filteredEvents.map((event) => (
          <MilestoneCard
            key={event.id}
            event={event}
            onInspectDocument={onInspectDocument}
          />
        ))}

        {filteredEvents.length === 0 && (
          <div className="text-center py-12 rounded-xl bg-zinc-900/40 border border-zinc-800 text-zinc-400 text-xs">
            No events match the selected filter.
          </div>
        )}
      </div>
    </div>
  );
};
