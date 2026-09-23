import React from "react";
import { LucideIcon } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  badgeText?: string;
  badgeType?: "neutral" | "emerald" | "amber" | "rose";
}

export function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  badgeText,
  badgeType = "neutral",
}: MetricCardProps) {
  const badgeColors = {
    neutral: "bg-surface-subtle text-zinc-400 border-surface-border",
    emerald: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    amber: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    rose: "bg-rose-500/10 text-rose-400 border-rose-500/20",
  };

  return (
    <Card className="p-5 flex flex-col justify-between hover:border-zinc-700/80 transition-all group">
      <div className="flex items-start justify-between">
        <span className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
          {title}
        </span>
        <div className="w-8 h-8 rounded-lg bg-surface-subtle border border-surface-border flex items-center justify-center text-zinc-400 group-hover:text-zinc-200 group-hover:border-zinc-700 transition-colors">
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div className="mt-4">
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold tracking-tight text-white font-mono">
            {value}
          </span>
          {badgeText && (
            <span
              className={cn(
                "text-[10px] font-medium px-2 py-0.5 rounded-full border",
                badgeColors[badgeType]
              )}
            >
              {badgeText}
            </span>
          )}
        </div>
        {subtitle && (
          <p className="text-xs text-zinc-500 mt-1 leading-normal">{subtitle}</p>
        )}
      </div>
    </Card>
  );
}
