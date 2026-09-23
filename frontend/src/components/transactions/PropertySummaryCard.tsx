import React from "react";
import {
  Building2,
  MapPin,
  Calendar,
  Maximize2,
  Tag,
  AlertTriangle,
} from "lucide-react";
import { PropertySummary } from "@/types/transaction";
import { Card } from "@/components/ui/Card";
import { formatCurrency, formatDate } from "@/lib/utils";

interface PropertySummaryCardProps {
  property: PropertySummary;
  className?: string;
}

export function PropertySummaryCard({
  property,
  className,
}: PropertySummaryCardProps) {
  const hasAreaMismatch =
    property.advertisedCarpetAreaSqFt &&
    property.advertisedCarpetAreaSqFt !== property.carpetAreaSqFt;

  return (
    <Card className={className}>
      <div className="p-5 border-b border-surface-border flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-surface-subtle border border-surface-border flex items-center justify-center text-zinc-300">
            <Building2 className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white tracking-tight">
              {property.project}
            </h2>
            <div className="flex items-center gap-1.5 text-xs text-zinc-400 mt-0.5">
              <MapPin className="w-3.5 h-3.5 text-zinc-500" />
              <span>{property.location}</span>
            </div>
          </div>
        </div>

        <div className="text-right">
          <span className="text-[10px] uppercase font-semibold text-zinc-500 tracking-wider block">
            Agreed Consideration
          </span>
          <span className="text-xl font-bold font-mono text-emerald-400">
            {formatCurrency(property.salePrice)}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-5 text-xs">
        {/* Unit & Floor */}
        <div className="space-y-1">
          <span className="text-zinc-500 font-medium uppercase tracking-wider text-[10px]">
            Unit / Tower
          </span>
          <p className="font-semibold text-zinc-200">{property.unit}</p>
          <p className="text-[11px] text-zinc-400">
            {property.tower} • Floor {property.floor}
          </p>
        </div>

        {/* Carpet Area */}
        <div className="space-y-1">
          <div className="flex items-center gap-1">
            <span className="text-zinc-500 font-medium uppercase tracking-wider text-[10px]">
              Carpet Area
            </span>
            {hasAreaMismatch && (
              <span className="text-amber-400" title="Mismatch with brochure">
                <AlertTriangle className="w-3 h-3" />
              </span>
            )}
          </div>
          <p className="font-semibold text-zinc-200 font-mono">
            {property.carpetAreaSqFt} sq. ft.
          </p>
          {hasAreaMismatch ? (
            <p className="text-[10px] text-amber-400/90 font-medium">
              Brochure: {property.advertisedCarpetAreaSqFt} sq. ft. (Mismatch)
            </p>
          ) : (
            <p className="text-[11px] text-zinc-500">
              Super: {property.superAreaSqFt} sq. ft.
            </p>
          )}
        </div>

        {/* Possession Date */}
        <div className="space-y-1">
          <span className="text-zinc-500 font-medium uppercase tracking-wider text-[10px]">
            Target Possession
          </span>
          <p className="font-semibold text-zinc-200">
            {formatDate(property.possessionDate)}
          </p>
          <p className="text-[11px] text-zinc-500">
            +{property.gracePeriodMonths} months grace period
          </p>
        </div>

        {/* Developer Entity */}
        <div className="space-y-1">
          <span className="text-zinc-500 font-medium uppercase tracking-wider text-[10px]">
            Promoter / Developer
          </span>
          <p className="font-semibold text-zinc-200 truncate">
            {property.developer}
          </p>
          <p className="text-[11px] text-emerald-400 font-medium">
            RERA Registered
          </p>
        </div>
      </div>
    </Card>
  );
}
