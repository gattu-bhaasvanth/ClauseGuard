"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  FilePlus2,
  Building2,
  UploadCloud,
  CheckCircle2,
  ArrowRight,
  ArrowLeft,
  Shield,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DocumentDropzone, SelectedFileItem } from "@/components/documents/DocumentDropzone";
import { LegalDisclaimerNotice } from "@/components/shared/LegalDisclaimerNotice";

export default function NewTransactionPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<1 | 2 | 3>(1);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form State
  const [formData, setFormData] = useState({
    projectName: "SkyView Residency",
    unit: "Flat A-1204",
    developer: "Skyline Urban Developers Pvt. Ltd.",
    city: "Gurgaon, Haryana",
    propertyType: "Residential Apartment",
    approxPrice: "₹ 1,42,50,000",
  });

  const [files, setFiles] = useState<SelectedFileItem[]>([]);

  const handleNextStep = () => {
    if (currentStep < 3) {
      setCurrentStep((prev) => (prev + 1) as 1 | 2 | 3);
    } else {
      // Simulate analysis launch
      setIsSubmitting(true);
      setTimeout(() => {
        router.push("/dashboard/transactions/skyview-a1204");
      }, 1200);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-surface-border">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold text-emerald-400 font-mono">
              Step {currentStep} of 3
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Start a Property Transaction
          </h1>
          <p className="text-xs text-zinc-400 mt-1 max-w-xl">
            Upload the documents associated with a property transaction and let ClauseGuard analyze them together.
          </p>
        </div>

        <Link href="/dashboard">
          <Button variant="ghost" size="sm" className="text-xs text-zinc-400">
            Cancel
          </Button>
        </Link>
      </div>

      {/* Stepper Progress Indicator */}
      <div className="grid grid-cols-3 gap-2">
        {[
          { num: 1, label: "1. Property Information" },
          { num: 2, label: "2. Upload Documents" },
          { num: 3, label: "3. Review & Analyze" },
        ].map((step) => {
          const isActive = currentStep === step.num;
          const isDone = currentStep > step.num;

          return (
            <div
              key={step.num}
              onClick={() => {
                if (isDone) setCurrentStep(step.num as 1 | 2 | 3);
              }}
              className={`p-3 rounded-lg border text-xs font-medium transition-all ${
                isActive
                  ? "border-emerald-500 bg-emerald-500/10 text-emerald-300 font-semibold"
                  : isDone
                  ? "border-surface-border bg-surface-subtle text-zinc-300 cursor-pointer"
                  : "border-surface-border/50 bg-surface/30 text-zinc-600 cursor-not-allowed"
              }`}
            >
              <span>{step.label}</span>
            </div>
          );
        })}
      </div>

      {/* STEP 1: Property Metadata */}
      {currentStep === 1 && (
        <Card className="p-6 space-y-5">
          <div className="flex items-center gap-2 border-b border-surface-border pb-3">
            <Building2 className="w-4 h-4 text-emerald-400" />
            <h2 className="text-sm font-semibold text-zinc-100">
              Basic Property & Transaction Identification
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="space-y-1.5">
              <label className="text-zinc-300 font-medium block">
                Project / Building Name
              </label>
              <input
                type="text"
                value={formData.projectName}
                onChange={(e) =>
                  setFormData({ ...formData, projectName: e.target.value })
                }
                className="w-full px-3 py-2 rounded-lg bg-zinc-900 border border-zinc-700 text-zinc-200 text-xs focus:outline-none focus:border-emerald-500"
                placeholder="e.g. SkyView Residency"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-300 font-medium block">
                Unit / Flat / Plot Identifier
              </label>
              <input
                type="text"
                value={formData.unit}
                onChange={(e) =>
                  setFormData({ ...formData, unit: e.target.value })
                }
                className="w-full px-3 py-2 rounded-lg bg-zinc-900 border border-zinc-700 text-zinc-200 text-xs focus:outline-none focus:border-emerald-500"
                placeholder="e.g. Flat A-1204"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-300 font-medium block">
                Promoter / Developer Name
              </label>
              <input
                type="text"
                value={formData.developer}
                onChange={(e) =>
                  setFormData({ ...formData, developer: e.target.value })
                }
                className="w-full px-3 py-2 rounded-lg bg-zinc-900 border border-zinc-700 text-zinc-200 text-xs focus:outline-none focus:border-emerald-500"
                placeholder="e.g. Skyline Urban Developers Pvt. Ltd."
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-300 font-medium block">
                City / Jurisdiction
              </label>
              <input
                type="text"
                value={formData.city}
                onChange={(e) =>
                  setFormData({ ...formData, city: e.target.value })
                }
                className="w-full px-3 py-2 rounded-lg bg-zinc-900 border border-zinc-700 text-zinc-200 text-xs focus:outline-none focus:border-emerald-500"
                placeholder="e.g. Gurgaon, Haryana"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-300 font-medium block">
                Approximate Agreed Consideration
              </label>
              <input
                type="text"
                value={formData.approxPrice}
                onChange={(e) =>
                  setFormData({ ...formData, approxPrice: e.target.value })
                }
                className="w-full px-3 py-2 rounded-lg bg-zinc-900 border border-zinc-700 text-zinc-200 text-xs focus:outline-none focus:border-emerald-500"
                placeholder="e.g. ₹ 1,42,50,000"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-300 font-medium block">
                Property Category
              </label>
              <select
                value={formData.propertyType}
                onChange={(e) =>
                  setFormData({ ...formData, propertyType: e.target.value })
                }
                className="w-full px-3 py-2 rounded-lg bg-zinc-900 border border-zinc-700 text-zinc-200 text-xs focus:outline-none focus:border-emerald-500"
              >
                <option value="Residential Apartment">Residential Apartment</option>
                <option value="Independent Villa">Independent Villa</option>
                <option value="Plotted Development">Plotted Development</option>
                <option value="Commercial Office / Retail">Commercial Office / Retail</option>
              </select>
            </div>
          </div>
        </Card>
      )}

      {/* STEP 2: Document Dropzone */}
      {currentStep === 2 && (
        <div className="space-y-4">
          <DocumentDropzone onFilesChanged={(f) => setFiles(f)} />
        </div>
      )}

      {/* STEP 3: Review & Initiate Analysis */}
      {currentStep === 3 && (
        <Card className="p-6 space-y-6">
          <div className="border-b border-surface-border pb-3">
            <h2 className="text-sm font-semibold text-zinc-100">
              Ready to Initiate Multi-Document Verification
            </h2>
            <p className="text-xs text-zinc-400 mt-0.5">
              ClauseGuard will process the documents together to generate your cross-document intelligence report.
            </p>
          </div>

          {/* Review Summary */}
          <div className="grid grid-cols-2 gap-4 text-xs p-4 rounded-lg bg-surface-subtle border border-surface-border">
            <div>
              <span className="text-[10px] text-zinc-400 uppercase font-semibold block">
                Property
              </span>
              <p className="font-semibold text-zinc-100">
                {formData.projectName} ({formData.unit})
              </p>
              <p className="text-zinc-400 text-[11px]">{formData.developer}</p>
            </div>
            <div>
              <span className="text-[10px] text-zinc-400 uppercase font-semibold block">
                Documents in Bundle
              </span>
              <p className="font-semibold text-emerald-400 font-mono">
                3 Documents Configured
              </p>
              <p className="text-zinc-400 text-[11px]">
                BBA, Allotment Letter, Brochure
              </p>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-zinc-900/80 border border-zinc-800 text-xs space-y-2">
            <span className="font-semibold text-zinc-200 block">
              What will be analyzed:
            </span>
            <ul className="space-y-1 text-zinc-400 text-[11px] list-disc list-inside">
              <li>Carpet area and super built-up area variance checks</li>
              <li>Delivery timelines and unconditional grace period clauses</li>
              <li>Asymmetry in late payment interest vs. delayed handover compensation</li>
              <li>Earnest money cancellation and forfeiture exposure</li>
            </ul>
          </div>

          <LegalDisclaimerNotice variant="banner" />
        </Card>
      )}

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between pt-4 border-t border-surface-border">
        {currentStep > 1 ? (
          <Button
            variant="outline"
            size="md"
            onClick={() => setCurrentStep((prev) => (prev - 1) as 1 | 2 | 3)}
            className="gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Previous</span>
          </Button>
        ) : (
          <div />
        )}

        <Button
          variant="emerald"
          size="md"
          isLoading={isSubmitting}
          onClick={handleNextStep}
          className="gap-2"
        >
          {currentStep === 3 ? (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Launch Transaction Intelligence</span>
            </>
          ) : (
            <>
              <span>Continue</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
