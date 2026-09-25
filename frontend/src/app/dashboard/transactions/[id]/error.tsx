"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { AlertTriangle, RefreshCw, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

export default function TransactionErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Transaction Error Boundary caught error:", error);
  }, [error]);

  return (
    <div className="max-w-2xl mx-auto py-12 px-4">
      <Card className="p-6 border-rose-500/30 bg-surface space-y-4 text-center">
        <div className="w-12 h-12 rounded-full bg-rose-500/10 border border-rose-500/20 flex items-center justify-center mx-auto text-rose-400">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-base font-semibold text-zinc-100">
            Unable to Display Transaction Intelligence
          </h2>
          <p className="text-xs text-zinc-400 mt-1 max-w-md mx-auto">
            {error?.message || "An unexpected error occurred while loading this transaction."}
          </p>
        </div>
        <div className="flex items-center justify-center gap-3 pt-2">
          <Button variant="emerald" size="sm" onClick={() => reset()} className="gap-2 text-xs">
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Try Again</span>
          </Button>
          <Link href="/dashboard/transactions">
            <Button variant="secondary" size="sm" className="gap-2 text-xs">
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Transactions</span>
            </Button>
          </Link>
        </div>
      </Card>
    </div>
  );
}
