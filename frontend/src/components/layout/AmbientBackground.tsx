import React from "react";

/**
 * AmbientBackground
 * Provides a restrained, professional enterprise SaaS visual background:
 * - Subtle ambient radial gradient drift (emerald & teal hues, ultra-low opacity)
 * - Restrained architectural micro-grid with radial mask
 * - Pure CSS hardware-accelerated transforms respecting prefers-reduced-motion
 */
export function AmbientBackground() {
  return (
    <div
      aria-hidden="true"
      className="fixed inset-0 -z-10 pointer-events-none overflow-hidden select-none"
    >
      {/* Ambient gradient layer 1: Top-center emerald/teal glow */}
      <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[920px] h-[520px] bg-gradient-to-tr from-emerald-500/[0.045] via-teal-500/[0.035] to-transparent blur-[140px] rounded-full motion-safe:animate-ambient-slow" />

      {/* Ambient gradient layer 2: Top-right subtle indigo/slate depth */}
      <div className="absolute top-1/4 -right-40 w-[640px] h-[520px] bg-gradient-to-bl from-emerald-600/[0.03] via-zinc-800/[0.03] to-transparent blur-[150px] rounded-full motion-safe:animate-ambient-reverse" />

      {/* Ambient gradient layer 3: Bottom-left soft foundation tint */}
      <div className="absolute -bottom-40 -left-40 w-[720px] h-[520px] bg-gradient-to-tr from-teal-500/[0.03] via-emerald-950/[0.04] to-transparent blur-[160px] rounded-full" />

      {/* Restrained enterprise architectural micro-grid with smooth radial mask fade */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#27272a08_1px,transparent_1px),linear-gradient(to_bottom,#27272a08_1px,transparent_1px)] bg-[size:48px_48px] [mask-image:radial-gradient(ellipse_70%_55%_at_50%_0%,#000_65%,transparent_100%)] opacity-80" />
    </div>
  );
}
