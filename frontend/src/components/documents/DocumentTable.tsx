import React from "react";
import Link from "next/link";
import { FileText, ArrowUpRight, CheckCircle2, AlertCircle } from "lucide-react";
import { TransactionDocument } from "@/types/transaction";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { formatDate } from "@/lib/utils";

interface DocumentTableProps {
  documents: TransactionDocument[];
  transactionId?: string;
}

export function DocumentTable({
  documents,
  transactionId = "skyview-a1204",
}: DocumentTableProps) {
  return (
    <Card className="overflow-hidden">
      <div className="p-4 border-b border-surface-border flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-zinc-100">
            Uploaded Transaction Documents ({documents.length})
          </h3>
          <p className="text-xs text-zinc-400">
            All files parsed together for cross-document consistency checks
          </p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-surface-subtle/50 text-zinc-400 uppercase tracking-wider text-[10px] border-b border-surface-border">
            <tr>
              <th className="py-3 px-4">Document File</th>
              <th className="py-3 px-4">Document Type</th>
              <th className="py-3 px-4">Pages / Size</th>
              <th className="py-3 px-4">Clauses Parsed</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-right">Viewer</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-border/60 text-zinc-300">
            {documents.map((doc) => (
              <tr
                key={doc.id}
                className="hover:bg-surface-hover/60 transition-colors"
              >
                <td className="py-3 px-4">
                  <div className="flex items-center gap-2.5">
                    <FileText className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                    <span className="font-medium text-zinc-100 truncate max-w-xs">
                      {doc.fileName}
                    </span>
                  </div>
                </td>
                <td className="py-3 px-4 text-zinc-400 font-mono text-[11px]">
                  {doc.documentType.replace(/_/g, " ")}
                </td>
                <td className="py-3 px-4 text-zinc-400">
                  {doc.pageCount} pages • {doc.fileSize}
                </td>
                <td className="py-3 px-4 font-mono text-zinc-200">
                  {doc.clauseCount} clauses
                </td>
                <td className="py-3 px-4">
                  <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 font-medium">
                    <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                    Indexed
                  </span>
                </td>
                <td className="py-3 px-4 text-right">
                  <Link
                    href={`/dashboard/transactions/${transactionId}/analysis?doc=${doc.id}`}
                  >
                    <Button variant="secondary" size="sm" className="h-7 text-xs gap-1">
                      <span>Open</span>
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
  );
}
