"use client";

import React from "react";
import Link from "next/link";
import { FileText, ArrowUpRight, CheckCircle2, UploadCloud, Search } from "lucide-react";
import { MOCK_SKYVIEW_TRANSACTION } from "@/mock/demoData";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export default function DocumentsPage() {
  const docs = MOCK_SKYVIEW_TRANSACTION.documents;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-surface-border">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Document Repository
          </h1>
          <p className="text-xs text-zinc-400 mt-1">
            All agreements, brochures, and schedules across your active transactions
          </p>
        </div>

        <Link href="/dashboard/transactions/new">
          <Button variant="emerald" size="sm" className="gap-1.5 text-xs">
            <UploadCloud className="w-3.5 h-3.5" />
            <span>Upload Documents</span>
          </Button>
        </Link>
      </div>

      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-surface-subtle/50 text-zinc-400 uppercase tracking-wider text-[10px] border-b border-surface-border">
              <tr>
                <th className="py-3 px-5">Document Name</th>
                <th className="py-3 px-5">Associated Transaction</th>
                <th className="py-3 px-5">Document Type</th>
                <th className="py-3 px-5">Pages / Size</th>
                <th className="py-3 px-5">OCR Status</th>
                <th className="py-3 px-5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-border/60 text-zinc-300">
              {docs.map((doc) => (
                <tr key={doc.id} className="hover:bg-surface-hover/60 transition-colors">
                  <td className="py-4 px-5">
                    <div className="flex items-center gap-2.5">
                      <FileText className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                      <span className="font-medium text-zinc-100">{doc.fileName}</span>
                    </div>
                  </td>
                  <td className="py-4 px-5 text-zinc-400">
                    SkyView Residency (A-1204)
                  </td>
                  <td className="py-4 px-5 font-mono text-[11px] text-zinc-400">
                    {doc.documentType.replace(/_/g, " ")}
                  </td>
                  <td className="py-4 px-5 text-zinc-400 font-mono">
                    {doc.pageCount} pgs • {doc.fileSize}
                  </td>
                  <td className="py-4 px-5">
                    <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 font-medium">
                      <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                      {doc.ocrStatus}
                    </span>
                  </td>
                  <td className="py-4 px-5 text-right">
                    <Link href={`/dashboard/transactions/skyview-a1204/analysis?doc=${doc.id}`}>
                      <Button variant="secondary" size="sm" className="h-7 text-xs gap-1">
                        <span>Open Viewer</span>
                        <ArrowUpRight className="w-3 h-3 text-zinc-400" />
                      </Button>
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
