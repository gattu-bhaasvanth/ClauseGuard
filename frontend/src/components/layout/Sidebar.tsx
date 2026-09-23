"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Layers,
  FilePlus2,
  FileText,
  BarChart3,
  FileSpreadsheet,
  Settings,
  Shield,
  ChevronRight,
  ExternalLink,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  className?: string;
  onClose?: () => void;
}

const NAV_ITEMS = [
  {
    name: "Overview",
    href: "/dashboard",
    icon: LayoutDashboard,
    exact: true,
  },
  {
    name: "Transactions",
    href: "/dashboard/transactions",
    icon: Layers,
    exact: false,
  },
  {
    name: "New Analysis",
    href: "/dashboard/transactions/new",
    icon: FilePlus2,
    exact: true,
    highlight: true,
  },
  {
    name: "Documents",
    href: "/dashboard/documents",
    icon: FileText,
    exact: true,
  },
  {
    name: "Insights",
    href: "/dashboard/insights",
    icon: BarChart3,
    exact: true,
  },
  {
    name: "Reports",
    href: "/dashboard/reports",
    icon: FileSpreadsheet,
    exact: true,
  },
  {
    name: "Settings",
    href: "/dashboard/settings",
    icon: Settings,
    exact: true,
  },
];

export function Sidebar({ className, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "w-64 flex-shrink-0 flex flex-col justify-between border-r border-surface-border bg-surface text-zinc-300 min-h-screen",
        className
      )}
    >
      {/* Top Brand Header */}
      <div>
        <div className="h-16 flex items-center justify-between px-5 border-b border-surface-border">
          <Link
            href="/"
            className="flex items-center gap-2.5 group"
            onClick={onClose}
          >
            <div className="w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 group-hover:border-emerald-500/60 transition-colors">
              <Shield className="w-4 h-4" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-sm tracking-tight text-white leading-none">
                ClauseGuard
              </span>
              <span className="text-[10px] text-zinc-400 font-mono mt-0.5">
                Transaction Intel
              </span>
            </div>
          </Link>
        </div>

        {/* Quick Demo Shortcut */}
        <div className="p-3">
          <Link
            href="/dashboard/transactions/skyview-a1204"
            onClick={onClose}
            className="flex items-center justify-between px-3 py-2 rounded-lg bg-surface-subtle border border-surface-border hover:border-zinc-700 transition-all text-xs group"
          >
            <div className="flex flex-col">
              <span className="text-[10px] uppercase font-semibold text-emerald-400 tracking-wider">
                Active Demo Bundle
              </span>
              <span className="font-medium text-zinc-200 truncate w-36">
                SkyView Flat A-1204
              </span>
            </div>
            <ChevronRight className="w-3.5 h-3.5 text-zinc-500 group-hover:text-zinc-200 transition-colors" />
          </Link>
        </div>

        {/* Primary Navigation Links */}
        <nav className="px-3 py-2 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = item.exact
              ? pathname === item.href
              : pathname.startsWith(item.href);

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onClose}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all group",
                  isActive
                    ? "bg-zinc-800 text-white font-semibold shadow-sm"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-surface-subtle",
                  item.highlight && !isActive && "text-emerald-400 hover:text-emerald-300"
                )}
              >
                <Icon
                  className={cn(
                    "w-4 h-4 transition-colors",
                    isActive
                      ? "text-emerald-400"
                      : item.highlight
                      ? "text-emerald-400"
                      : "text-zinc-500 group-hover:text-zinc-300"
                  )}
                />
                <span className="flex-1">{item.name}</span>
                {item.highlight && (
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Bottom Legal Status & User info */}
      <div className="p-3 border-t border-surface-border space-y-3">
        <div className="px-3 py-2 rounded-lg bg-surface-subtle/60 border border-surface-border/60 text-[11px] text-zinc-400">
          <div className="flex items-center justify-between mb-1">
            <span className="text-zinc-300 font-semibold">Phase 1 Frontend</span>
            <span className="text-emerald-400 text-[10px] font-mono">Demo Mode</span>
          </div>
          <p className="text-[10px] text-zinc-500 leading-tight">
            Next.js App Router with mock intelligence data.
          </p>
        </div>

        <Link
          href="/"
          className="flex items-center justify-between px-3 py-1.5 text-[11px] text-zinc-400 hover:text-zinc-200 transition-colors"
        >
          <span>Exit to Landing Page</span>
          <ExternalLink className="w-3 h-3 text-zinc-400" />
        </Link>
      </div>
    </aside>
  );
}
