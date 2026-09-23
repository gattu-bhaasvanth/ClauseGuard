import React from "react";
import Link from "next/link";
import { ArrowUpRight, FileText, AlertTriangle } from "lucide-react";
import { Transaction } from "@/types/transaction";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { formatCurrency, formatDate } from "@/lib/utils";

interface RecentTransactionsTableProps {
  transactions: Transaction[];
}

export function RecentTransactionsTable({
  transactions,
}: RecentTransactionsTableProps) {
  return (
    <Card className="overflow-hidden">
      <div className="p-5 border-b border-surface-border flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold text-zinc-100">
            Recent Property Transactions
          </h2>
          <p className="text-xs text-zinc-400 mt-0.5">
            Active multi-document analysis workspaces
          </p>
        </div>
        <Link href="/dashboard/transactions">
          <Button variant="ghost" size="sm" className="text-xs text-zinc-400">
            View All ({transactions.length})
          </Button>
        </Link>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-surface-subtle/60 text-zinc-400 font-medium border-b border-surface-border uppercase tracking-wider text-[10px]">
            <tr>
              <th className="py-3 px-5">Property / Unit</th>
              <th className="py-3 px-5">Developer</th>
              <th className="py-3 px-5">Health Score</th>
              <th className="py-3 px-5">Documents</th>
              <th className="py-3 px-5">Issues</th>
              <th className="py-3 px-5">Sale Price</th>
              <th className="py-3 px-5">Updated</th>
              <th className="py-3 px-5 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-border/60 text-zinc-300">
            {transactions.map((tx) => (
              <tr
                key={tx.id}
                className="hover:bg-surface-hover/60 transition-colors group"
              >
                <td className="py-4 px-5">
                  <div className="flex flex-col">
                    <span className="font-semibold text-zinc-100 group-hover:text-emerald-400 transition-colors">
                      {tx.property.project}
                    </span>
                    <span className="text-[11px] text-zinc-400">
                      {tx.property.unit} • Floor {tx.property.floor}
                    </span>
                  </div>
                </td>
                <td className="py-4 px-5 text-zinc-400 max-w-[180px] truncate">
                  {tx.property.developer}
                </td>
                <td className="py-4 px-5">
                  <div className="flex items-center gap-2">
                    <span
                      className={`font-mono font-bold ${
                        tx.healthScore >= 80
                          ? "text-emerald-400"
                          : tx.healthScore >= 65
                          ? "text-amber-400"
                          : "text-rose-400"
                      }`}
                    >
                      {tx.healthScore}
                    </span>
                    <span className="text-[10px] text-zinc-500">/100</span>
                  </div>
                </td>
                <td className="py-4 px-5">
                  <span className="inline-flex items-center gap-1 text-zinc-400 font-mono">
                    <FileText className="w-3.5 h-3.5 text-zinc-500" />
                    {tx.documentsCount}
                  </span>
                </td>
                <td className="py-4 px-5">
                  {tx.issuesCount > 0 ? (
                    <span className="inline-flex items-center gap-1 font-medium text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded text-[11px] border border-amber-500/20">
                      <AlertTriangle className="w-3 h-3 text-amber-400" />
                      {tx.issuesCount} issues
                    </span>
                  ) : (
                    <span className="text-zinc-500 text-[11px]">Clean</span>
                  )}
                </td>
                <td className="py-4 px-5 font-mono text-zinc-200">
                  {formatCurrency(tx.property.salePrice)}
                </td>
                <td className="py-4 px-5 text-zinc-500 text-[11px]">
                  {formatDate(tx.updatedAt)}
                </td>
                <td className="py-4 px-5 text-right">
                  <Link href={`/dashboard/transactions/${tx.id}`}>
                    <Button variant="secondary" size="sm" className="h-7 text-xs gap-1">
                      <span>View</span>
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
