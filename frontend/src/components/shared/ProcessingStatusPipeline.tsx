import React from "react";
import {
  UploadCloud,
  FileText,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  Loader2,
} from "lucide-react";
import { cn } from "@/lib/utils";

export type ProcessingStage =
  | "INGESTING"
  | "EXTRACTING"
  | "CLASSIFYING"
  | "VERIFYING"
  | "READY";

export interface ProcessingStatusPipelineProps {
  currentStage: ProcessingStage;
  variant?: "card" | "inline" | "modal";
  title?: string;
  subtitle?: string;
  className?: string;
}

const STAGES: {
  id: ProcessingStage;
  label: string;
  description: string;
  icon: React.ElementType;
}[] = [
  {
    id: "INGESTING",
    label: "Ingesting",
    description: "Registering document bundle",
    icon: UploadCloud,
  },
  {
    id: "EXTRACTING",
    label: "Extracting",
    description: "OCR & clause segmentation",
    icon: FileText,
  },
  {
    id: "CLASSIFYING",
    label: "Classifying",
    description: "Statutory classification & scoring",
    icon: Sparkles,
  },
  {
    id: "VERIFYING",
    label: "Verifying",
    description: "Cross-document risk verification",
    icon: ShieldCheck,
  },
  {
    id: "READY",
    label: "Ready",
    description: "Workspace initialized",
    icon: CheckCircle2,
  },
];

const STAGE_ORDER: Record<ProcessingStage, number> = {
  INGESTING: 0,
  EXTRACTING: 1,
  CLASSIFYING: 2,
  VERIFYING: 3,
  READY: 4,
};

export function ProcessingStatusPipeline({
  currentStage,
  variant = "card",
  title = "Analyzing Transaction Bundle",
  subtitle = "Executing multi-document verification pipeline",
  className,
}: ProcessingStatusPipelineProps) {
  const currentIndex = STAGE_ORDER[currentStage] ?? 0;
  const progressPercent = Math.round(((currentIndex + 1) / STAGES.length) * 100);

  return (
    <div
      className={cn(
        "rounded-2xl border border-surface-border bg-surface/95 backdrop-blur-md p-5 sm:p-6 shadow-2xl relative overflow-hidden transition-all duration-300",
        variant === "card" && "max-w-2xl mx-auto",
        className
      )}
    >
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-surface-border/80">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <span className="text-[11px] font-mono uppercase tracking-wider text-emerald-400 font-semibold">
              Live Pipeline Active
            </span>
          </div>
          <h3 className="text-base sm:text-lg font-bold text-white tracking-tight">
            {title}
          </h3>
          <p className="text-xs text-zinc-400 mt-0.5">{subtitle}</p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto bg-surface-subtle border border-surface-border px-3 py-1.5 rounded-lg text-xs font-mono text-zinc-300">
          <span>Stage {currentIndex + 1} of 5</span>
          <span className="text-emerald-400 font-semibold">({progressPercent}%)</span>
        </div>
      </div>

      {/* Progress Bar Track */}
      <div className="w-full bg-zinc-800/80 h-1.5 rounded-full overflow-hidden my-5">
        <div
          className="h-full bg-gradient-to-r from-emerald-500 via-teal-400 to-emerald-400 rounded-full transition-all duration-500 ease-out"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* 5 Stepper Milestones */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 pt-1">
        {STAGES.map((stage, idx) => {
          const isDone = idx < currentIndex;
          const isCurrent = idx === currentIndex;
          const isPending = idx > currentIndex;
          const Icon = stage.icon;

          return (
            <div
              key={stage.id}
              className={cn(
                "flex flex-col items-center sm:items-start p-2.5 rounded-xl border text-center sm:text-left transition-all duration-300",
                isCurrent &&
                  "bg-emerald-500/10 border-emerald-500/40 shadow-subtle-glow",
                isDone &&
                  "bg-surface-subtle/80 border-surface-border text-zinc-300",
                isPending &&
                  "bg-surface-subtle/30 border-surface-border/40 text-zinc-600 opacity-60"
              )}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <div
                  className={cn(
                    "w-6 h-6 rounded-lg flex items-center justify-center text-xs transition-colors",
                    isCurrent && "bg-emerald-500 text-zinc-950 font-bold",
                    isDone && "bg-emerald-500/20 text-emerald-400",
                    isPending && "bg-zinc-800 text-zinc-500"
                  )}
                >
                  {isCurrent ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : isDone ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  ) : (
                    <Icon className="w-3.5 h-3.5" />
                  )}
                </div>
                <span
                  className={cn(
                    "text-xs font-semibold",
                    isCurrent && "text-emerald-300",
                    isDone && "text-zinc-200",
                    isPending && "text-zinc-500"
                  )}
                >
                  {stage.label}
                </span>
              </div>
              <span className="text-[10px] text-zinc-400 leading-tight hidden sm:block">
                {stage.description}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
