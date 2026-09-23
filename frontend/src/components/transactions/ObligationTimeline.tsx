import React from "react";
import { Calendar, DollarSign, CheckCircle2, Clock } from "lucide-react";
import { ImportantDate, PaymentObligation } from "@/types/transaction";
import { Card } from "@/components/ui/Card";
import { formatCurrency, formatDate } from "@/lib/utils";

interface ObligationTimelineProps {
  dates: ImportantDate[];
  payments: PaymentObligation[];
}

export function ObligationTimeline({ dates, payments }: ObligationTimelineProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Important Dates Column */}
      <Card className="p-5">
        <div className="flex items-center gap-2 mb-4">
          <Calendar className="w-4 h-4 text-emerald-400" />
          <h3 className="text-sm font-semibold text-zinc-100">
            Important Dates & Milestones
          </h3>
        </div>

        <div className="space-y-4">
          {dates.map((d) => (
            <div
              key={d.id}
              className="flex items-start gap-3 p-3 rounded-lg bg-surface-subtle border border-surface-border text-xs"
            >
              <div className="w-8 h-8 rounded-md bg-zinc-800 border border-zinc-700 flex items-center justify-center text-zinc-300 font-mono text-[11px] flex-shrink-0">
                <Clock className="w-4 h-4 text-zinc-400" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-zinc-200">{d.title}</span>
                  <span className="font-mono text-emerald-400 font-medium">
                    {formatDate(d.date)}
                  </span>
                </div>
                <p className="text-[11px] text-zinc-400 mt-1">{d.description}</p>
                <span className="text-[10px] text-zinc-500 font-mono block mt-1">
                  Source: {d.sourceDoc}
                </span>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Payment Obligations Column */}
      <Card className="p-5">
        <div className="flex items-center gap-2 mb-4">
          <DollarSign className="w-4 h-4 text-emerald-400" />
          <h3 className="text-sm font-semibold text-zinc-100">
            Payment Obligations & Cash-Flow Schedule
          </h3>
        </div>

        <div className="space-y-3">
          {payments.map((p) => (
            <div
              key={p.id}
              className="p-3 rounded-lg bg-surface-subtle border border-surface-border flex items-center justify-between text-xs"
            >
              <div className="flex items-center gap-3">
                {p.status === "PAID" ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                ) : (
                  <div className="w-4 h-4 rounded-full border-2 border-amber-400/60 flex-shrink-0" />
                )}
                <div>
                  <span className="font-medium text-zinc-200 block">
                    {p.milestoneTitle}
                  </span>
                  <span className="text-[10px] text-zinc-500">
                    {p.dueDateCondition} • {p.clauseCitation}
                  </span>
                </div>
              </div>

              <div className="text-right">
                <span className="font-mono font-semibold text-zinc-100 block">
                  {formatCurrency(p.amount)}
                </span>
                <span className="text-[10px] text-zinc-400 font-mono">
                  {p.percentage}% Total
                </span>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
