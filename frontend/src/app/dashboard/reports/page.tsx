"use client";

import React from "react";
import Link from "next/link";
import { FileSpreadsheet, Download, ExternalLink, Shield } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { LegalDisclaimerNotice } from "@/components/shared/LegalDisclaimerNotice";

export default function ReportsPage() {
  return (
    <div className="space-y-6">
      <div className="pb-4 border-b border-surface-border">
        <h1 className="text-2xl font-bold tracking-tight text-white">
          Transaction Audit Reports
        </h1>
        <p className="text-xs text-zinc-400 mt-1">
          Exportable evidence-backed summaries for legal advisors and property buyers
        </p>
      </div>

      <div className="space-y-4">
        {[
          {
            title: "Comprehensive Transaction Intelligence Report — SkyView Flat A-1204",
            date: "Generated on 23 Sep 2026",
            findingsCount: "2 Inconsistencies, 4 Critical Risks",
            pages: "18 pages",
          },
          {
            title: "Cross-Document Discrepancy Matrix — SkyView Flat A-1204",
            date: "Generated on 23 Sep 2026",
            findingsCount: "Carpet Area & Possession Mismatches",
            pages: "6 pages",
          },
          {
            title: "Cash-Flow & Milestone Schedule Audit — SkyView Flat A-1204",
            date: "Generated on 22 Sep 2026",
            findingsCount: "5 Milestones, Total ₹1.42 Cr",
            pages: "4 pages",
          },
        ].map((report, idx) => (
          <Card key={idx} className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-lg bg-surface-subtle border border-surface-border flex items-center justify-center text-emerald-400 flex-shrink-0">
                <FileSpreadsheet className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-zinc-100">{report.title}</h3>
                <div className="flex items-center gap-2 text-[11px] text-zinc-400 mt-1">
                  <span>{report.date}</span>
                  <span>•</span>
                  <span>{report.findingsCount}</span>
                  <span>•</span>
                  <span className="font-mono">{report.pages}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Link href="/dashboard/transactions/skyview-a1204">
                <Button variant="secondary" size="sm" className="text-xs">
                  <span>View Online</span>
                </Button>
              </Link>
              <Button variant="outline" size="sm" className="text-xs gap-1.5">
                <Download className="w-3.5 h-3.5" />
                <span>PDF Export</span>
              </Button>
            </div>
          </Card>
        ))}
      </div>

      <LegalDisclaimerNotice variant="banner" />
    </div>
  );
}
