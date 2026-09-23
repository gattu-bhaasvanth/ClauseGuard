"use client";

import React from "react";
import Link from "next/link";
import { Search, Plus, Bell, Menu, Shield } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface DashboardHeaderProps {
  onMenuToggle?: () => void;
  title?: string;
  subtitle?: string;
}

export function DashboardHeader({
  onMenuToggle,
  title,
  subtitle,
}: DashboardHeaderProps) {
  return (
    <header className="h-16 border-b border-surface-border bg-surface/50 backdrop-blur-sm px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3">
        {onMenuToggle && (
          <button
            onClick={onMenuToggle}
            className="md:hidden p-2 text-zinc-400 hover:text-white rounded-lg hover:bg-surface-subtle"
            aria-label="Toggle navigation"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

        <div>
          {title ? (
            <div className="flex flex-col">
              <h1 className="text-sm font-semibold text-zinc-100 leading-tight">
                {title}
              </h1>
              {subtitle && (
                <span className="text-[11px] text-zinc-400">{subtitle}</span>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-md bg-surface-subtle border border-surface-border text-xs text-zinc-400">
                <Search className="w-3.5 h-3.5 text-zinc-400" />
                <span>Search transactions, documents, or clauses...</span>
                <kbd className="text-[10px] bg-zinc-800 text-zinc-400 px-1.5 py-0.5 rounded border border-zinc-700 font-mono">
                  ⌘K
                </kbd>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <Link href="/dashboard/transactions/new">
          <Button variant="emerald" size="sm" className="hidden sm:flex gap-1.5">
            <Plus className="w-3.5 h-3.5" />
            <span>New Transaction</span>
          </Button>
        </Link>

        {/* Informational shield */}
        <div className="hidden lg:flex items-center gap-1.5 px-2 py-1 rounded bg-surface-subtle border border-surface-border text-[11px] text-zinc-400">
          <Shield className="w-3 h-3 text-emerald-400" />
          <span>Informational System</span>
        </div>

        {/* Notification simulated icon */}
        <button
          className="p-2 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-surface-subtle transition-colors relative"
          aria-label="Notifications"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-emerald-400" />
        </button>

        {/* User avatar indicator */}
        <div className="w-8 h-8 rounded-full bg-zinc-800 border border-surface-border flex items-center justify-center text-xs font-semibold text-zinc-300">
          BG
        </div>
      </div>
    </header>
  );
}
