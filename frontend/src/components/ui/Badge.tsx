import * as React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "secondary" | "outline" | "emerald" | "amber" | "rose" | "purple" | "blue";
}

export function Badge({
  className,
  variant = "default",
  children,
  ...props
}: BadgeProps) {
  const base =
    "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium transition-colors";

  const variants = {
    default: "bg-surface-subtle text-zinc-300 border border-surface-border",
    secondary: "bg-zinc-800 text-zinc-300 border border-zinc-700/60",
    outline: "bg-transparent text-zinc-400 border border-surface-border",
    emerald: "bg-emerald-500/10 text-emerald-400 border border-emerald-500/25",
    amber: "bg-amber-500/10 text-amber-400 border border-amber-500/25",
    rose: "bg-rose-500/10 text-rose-400 border border-rose-500/25",
    purple: "bg-purple-500/10 text-purple-400 border border-purple-500/25",
    blue: "bg-blue-500/10 text-blue-400 border border-blue-500/25",
  };

  return (
    <span className={cn(base, variants[variant], className)} {...props}>
      {children}
    </span>
  );
}
