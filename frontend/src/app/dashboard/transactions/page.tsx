"use client";

import React, { useState, useEffect, useMemo, useCallback } from "react";
import Link from "next/link";
import { Plus, Search, Filter, Layers, ArrowUpRight, Loader2, RotateCw, X } from "lucide-react";
import { Transaction } from "@/types/transaction";
import { fetchTransactions } from "@/lib/api";
import { RecentTransactionsTable } from "@/components/dashboard/RecentTransactionsTable";
import { Button } from "@/components/ui/Button";

export default function TransactionsListPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [allTransactions, setAllTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadTransactions = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);

    try {
      const data = await fetchTransactions();
      if (Array.isArray(data)) {
        setAllTransactions(data);
      }
    } catch (err) {
      console.error("Failed to load transactions:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadTransactions();
  }, [loadTransactions]);

  // Comprehensive multi-field client-side search over persisted transactions
  const filteredTransactions = useMemo(() => {
    if (!searchTerm.trim()) return allTransactions;
    const q = searchTerm.trim().toLowerCase();
    return allTransactions.filter((t) => {
      const titleMatch = t.title?.toLowerCase().includes(q);
      const projectMatch = t.property?.project?.toLowerCase().includes(q);
      const developerMatch = t.property?.developer?.toLowerCase().includes(q);
      const unitMatch = t.property?.unit?.toLowerCase().includes(q);
      const locationMatch = t.property?.location?.toLowerCase().includes(q);
      const idMatch = t.id?.toLowerCase().includes(q);
      return (
        titleMatch ||
        projectMatch ||
        developerMatch ||
        unitMatch ||
        locationMatch ||
        idMatch
      );
    });
  }, [allTransactions, searchTerm]);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-surface-border">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-bold tracking-tight text-white">
              Property Transactions
            </h1>
            {!loading && (
              <span className="px-2 py-0.5 rounded-full text-[11px] font-mono font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                {searchTerm.trim()
                  ? `${filteredTransactions.length} of ${allTransactions.length} found`
                  : `${allTransactions.length} workspaces`}
              </span>
            )}
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Manage your property document bundles and review multi-document audit reports
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => loadTransactions(true)}
            disabled={loading || refreshing}
            className="h-8 text-xs text-zinc-400 hover:text-zinc-200 gap-1.5"
            title="Refresh transaction list from database"
          >
            <RotateCw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin" : ""}`} />
            <span className="hidden sm:inline">Refresh</span>
          </Button>
          <Link href="/dashboard/transactions/new">
            <Button variant="emerald" size="sm" className="gap-1.5 text-xs h-8">
              <Plus className="w-3.5 h-3.5" />
              <span>Start New Transaction</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Filter / Search Bar */}
      <div className="flex items-center gap-3">
        <div className="flex-1 relative">
          <Search className="w-4 h-4 text-zinc-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by project name, developer, or unit number (e.g., 'Maple Heights', 'Northstar', 'B-904')..."
            className="w-full pl-9 pr-9 py-2 rounded-lg bg-surface border border-surface-border text-xs text-zinc-200 placeholder:text-zinc-500 focus:outline-none focus:border-emerald-500 transition-colors"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-200 transition-colors"
              title="Clear search"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Transactions Table or Loading State */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 rounded-xl bg-surface border border-surface-border">
          <Loader2 className="w-6 h-6 text-emerald-400 animate-spin mb-3" />
          <p className="text-xs font-medium text-zinc-300">
            Loading property transaction workspaces...
          </p>
          <p className="text-[11px] text-zinc-500 mt-1">
            Querying persistent transaction bundles from local database
          </p>
        </div>
      ) : (
        <RecentTransactionsTable transactions={filteredTransactions} />
      )}
    </div>
  );
}
