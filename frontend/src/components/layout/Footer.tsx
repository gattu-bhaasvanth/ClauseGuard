import React from "react";
import Link from "next/link";
import { Shield } from "lucide-react";
import { LegalDisclaimerNotice } from "@/components/shared/LegalDisclaimerNotice";

export function Footer() {
  return (
    <footer className="border-t border-surface-border bg-surface/50 text-zinc-400">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
          {/* Brand info */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                <Shield className="w-3.5 h-3.5" />
              </div>
              <span className="font-bold text-white tracking-tight">ClauseGuard</span>
            </div>
            <p className="text-xs text-zinc-400 max-w-md leading-relaxed">
              AI-Powered Real-Estate Transaction Intelligence. Analyzing property agreements, allotment letters, payment schedules, and marketing brochures together to detect inconsistencies and critical risks before you sign.
            </p>
          </div>

          {/* Product links */}
          <div className="space-y-2 text-xs">
            <span className="font-semibold text-zinc-200 block uppercase tracking-wider text-[10px]">
              Platform
            </span>
            <ul className="space-y-1.5">
              <li>
                <Link href="/dashboard" className="hover:text-zinc-100 transition-colors">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link href="/dashboard/transactions/new" className="hover:text-zinc-100 transition-colors">
                  New Transaction
                </Link>
              </li>
              <li>
                <Link href="/dashboard/transactions/skyview-a1204" className="hover:text-zinc-100 transition-colors">
                  Sample Transaction
                </Link>
              </li>
              <li>
                <Link href="/dashboard/transactions/skyview-a1204/analysis" className="hover:text-zinc-100 transition-colors">
                  Split Document Viewer
                </Link>
              </li>
            </ul>
          </div>

          {/* Architecture & Intelligence */}
          <div className="space-y-2 text-xs">
            <span className="font-semibold text-zinc-200 block uppercase tracking-wider text-[10px]">
              Architecture & Intelligence
            </span>
            <ul className="space-y-1.5 text-zinc-400">
              <li className="text-emerald-400/90 font-medium">Document Ingestion & OCR</li>
              <li>Clause & Entity Intelligence</li>
              <li>Cross-Document Verification</li>
              <li>Risk & Audit Analysis</li>
              <li>Grounded RAG & Evidence</li>
              <li>Domain-Specific ML</li>
              <li>Transaction Intelligence Copilot</li>
              <li>Timeline, Lineage & Executive Brief</li>
            </ul>
          </div>
        </div>

        {/* Informational Legal Notice */}
        <LegalDisclaimerNotice variant="footer" />

        <div className="mt-8 pt-4 border-t border-surface-border/50 flex flex-col sm:flex-row items-center justify-between text-[11px] text-zinc-500">
          <span>&copy; {new Date().getFullYear()} ClauseGuard. Built for transparent property transactions.</span>
          <span className="mt-2 sm:mt-0 font-mono">v1.0.0 • Transaction Intelligence</span>
        </div>
      </div>
    </footer>
  );
}
