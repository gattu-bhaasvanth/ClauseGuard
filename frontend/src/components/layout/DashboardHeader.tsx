"use client";

import React, { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { Search, Plus, Bell, Menu, Shield, BellOff, X } from "lucide-react";
import { Button } from "@/components/ui/Button";

export interface HeaderAlert {
  id: string;
  title: string;
  description: string;
  severity?: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  timestamp?: string;
  link?: string;
}

interface DashboardHeaderProps {
  onMenuToggle?: () => void;
  title?: string;
  subtitle?: string;
  alerts?: HeaderAlert[];
}

export function DashboardHeader({
  onMenuToggle,
  title,
  subtitle,
  alerts = [],
}: DashboardHeaderProps) {
  const [alertsOpen, setAlertsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!alertsOpen) return;

    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setAlertsOpen(false);
      }
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setAlertsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [alertsOpen]);

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

        {/* Notification Bell with Dropdown Popover */}
        <div className="relative" ref={dropdownRef}>
          <button
            id="alerts-bell-button"
            onClick={() => setAlertsOpen((prev) => !prev)}
            className={`p-2 rounded-lg transition-colors relative ${
              alertsOpen
                ? "text-zinc-100 bg-surface-subtle"
                : "text-zinc-400 hover:text-zinc-200 hover:bg-surface-subtle"
            }`}
            aria-label="Notifications"
            aria-expanded={alertsOpen}
            aria-haspopup="true"
          >
            <Bell className="w-4 h-4" />
            {alerts.length > 0 && (
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-emerald-400" />
            )}
          </button>

          {alertsOpen && (
            <div
              id="alerts-dropdown-panel"
              role="dialog"
              aria-label="Alerts & Notifications"
              className="absolute right-0 mt-2 w-80 sm:w-96 rounded-xl border border-surface-border bg-surface/95 backdrop-blur-md shadow-2xl p-4 z-50 animate-in fade-in zoom-in-95 duration-150"
            >
              <div className="flex items-center justify-between pb-3 border-b border-surface-border">
                <div className="flex items-center gap-2">
                  <h3 className="text-xs font-semibold text-zinc-100">
                    Alerts & Notifications
                  </h3>
                  <span className="px-1.5 py-0.2 rounded text-[10px] font-mono bg-zinc-800 text-zinc-400 border border-zinc-700">
                    {alerts.length}
                  </span>
                </div>
                <button
                  onClick={() => setAlertsOpen(false)}
                  className="text-zinc-400 hover:text-zinc-200 p-0.5 rounded transition-colors"
                  aria-label="Close alerts"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>

              {alerts.length === 0 ? (
                <div className="py-8 px-4 flex flex-col items-center justify-center text-center">
                  <div className="w-10 h-10 rounded-full bg-zinc-800/80 border border-surface-border flex items-center justify-center mb-3">
                    <BellOff className="w-5 h-5 text-zinc-400" />
                  </div>
                  <h4 className="text-xs font-semibold text-zinc-200 mb-1">
                    No new alerts
                  </h4>
                  <p className="text-[11px] text-zinc-400 leading-relaxed max-w-[260px]">
                    All property transaction monitors are clear. Document audit warnings and discrepancy alerts will appear here.
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-surface-border max-h-72 overflow-y-auto my-2">
                  {alerts.map((alert) => (
                    <div key={alert.id} className="py-2.5 px-1 flex flex-col gap-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-medium text-zinc-200">
                          {alert.title}
                        </span>
                        {alert.severity && (
                          <span
                            className={`text-[10px] px-1.5 py-0.5 rounded font-mono font-semibold ${
                              alert.severity === "CRITICAL" || alert.severity === "HIGH"
                                ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                                : alert.severity === "MEDIUM"
                                ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                                : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                            }`}
                          >
                            {alert.severity}
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-zinc-400 leading-relaxed">
                        {alert.description}
                      </p>
                      {alert.timestamp && (
                        <span className="text-[10px] text-zinc-500 font-mono">
                          {alert.timestamp}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}

              <div className="pt-2.5 border-t border-surface-border flex items-center justify-between text-[10px] text-zinc-500">
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span>Audit Engine Active</span>
                </div>
                <span>ClauseGuard Real-Time</span>
              </div>
            </div>
          )}
        </div>

        {/* User avatar indicator */}
        <div className="w-8 h-8 rounded-full bg-zinc-800 border border-surface-border flex items-center justify-center text-xs font-semibold text-zinc-300">
          BG
        </div>
      </div>
    </header>
  );
}
