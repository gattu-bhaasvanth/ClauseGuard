import * as React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger" | "emerald";
  size?: "sm" | "md" | "lg" | "icon";
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = "primary",
      size = "md",
      isLoading,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const baseStyles =
      "inline-flex items-center justify-center font-medium rounded-lg transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500/50 disabled:opacity-50 disabled:pointer-events-none active:scale-[0.98]";

    const variants = {
      primary:
        "bg-zinc-100 text-zinc-950 hover:bg-white shadow-sm border border-zinc-200/20 font-semibold",
      secondary:
        "bg-surface-subtle text-zinc-200 hover:bg-surface-hover border border-surface-border",
      outline:
        "bg-transparent text-zinc-300 hover:text-white hover:bg-surface-hover border border-surface-border",
      ghost:
        "bg-transparent text-zinc-400 hover:text-zinc-100 hover:bg-surface-subtle",
      danger:
        "bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 border border-rose-500/30",
      emerald:
        "bg-emerald-500 text-zinc-950 hover:bg-emerald-400 font-semibold shadow-subtle-glow",
    };

    const sizes = {
      sm: "h-8 px-3 text-xs gap-1.5",
      md: "h-9 px-4 text-sm gap-2",
      lg: "h-11 px-5 text-base gap-2.5",
      icon: "h-9 w-9 p-0",
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {isLoading ? (
          <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
        ) : null}
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";
