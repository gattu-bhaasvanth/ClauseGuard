"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Plus, Search, Filter, Layers, ArrowUpRight } from "lucide-react";
import { MOCK_ALL_TRANSACTIONS } from "@/mock/demoData";
import { RecentTransactionsTable } from "@/components/dashboard/RecentTransactionsTable";
import { Button } from "@/components/ui/Button";

export default function TransactionsListPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const transactions = MOCK_ALL_TRANSACTIONS.filter(
    (t) =>
      t.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.property.project.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.property.developer.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-surface-border">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Property Transactions
          </h1>
          <p className="text-xs text-zinc-400 mt-1">
            Manage your property document bundles and review multi-document audit reports
          </p>
        </div>

        <Link href="/dashboard/transactions/new">
          <Button variant="emerald" size="sm" className="gap-1.5 text-xs">
            <Plus className="w-3.5 h-3.5" />
            <span>Start New Transaction</span>
          </Button>
        </Link>
      </div>

      {/* Filter / Search Bar */}
      <div className="flex items-center gap-3">
        <div className="flex-1 relative">
          <Search className="w-4 h-4 text-zinc-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by project name, developer, or unit number..."
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-surface border border-surface-border text-xs text-zinc-200 placeholder:text-zinc-500 focus:outline-none focus:border-emerald-500"
          />
        </div>
      </div>

      {/* Transactions Table */}
      <RecentTransactionsTable transactions={transactions} />
    </div>
  );
}
