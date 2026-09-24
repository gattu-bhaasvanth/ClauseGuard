"use client";

import React, { useState, useRef } from "react";
import {
  UploadCloud,
  FileText,
  Trash2,
  CheckCircle2,
  AlertCircle,
  FileCheck,
} from "lucide-react";
import { DocumentType } from "@/types/transaction";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/utils";

export interface SelectedFileItem {
  id: string;
  file: File;
  name: string;
  sizeFormatted: string;
  documentType: DocumentType;
  status: "READY" | "UPLOADING" | "ANALYZED";
}

export const DOCUMENT_TYPE_LABELS: { value: DocumentType; label: string; shortLabel: string }[] = [
  { value: "BUILDER_BUYER_AGREEMENT", label: "Builder-Buyer Agreement (BBA)", shortLabel: "BBA" },
  { value: "SALE_AGREEMENT", label: "Agreement for Sale", shortLabel: "Sale Agreement" },
  { value: "ALLOTMENT_LETTER", label: "Allotment Letter", shortLabel: "Allotment Letter" },
  { value: "PAYMENT_SCHEDULE", label: "Payment Schedule", shortLabel: "Payment Schedule" },
  { value: "PROJECT_BROCHURE", label: "Project Brochure / Floor Plan", shortLabel: "Brochure" },
  { value: "NOC_SANCTION_PLAN", label: "Sanction Plan / NOC", shortLabel: "Sanction Plan" },
  { value: "OTHER", label: "Other Supporting Document", shortLabel: "Other Document" },
];

interface DocumentDropzoneProps {
  onFilesChanged?: (files: SelectedFileItem[]) => void;
  className?: string;
  initialFiles?: SelectedFileItem[];
}

export function DocumentDropzone({
  onFilesChanged,
  className,
  initialFiles = [],
}: DocumentDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<SelectedFileItem[]>(initialFiles);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 KB";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
  };

  const inferDocumentType = (fileName: string): DocumentType => {
    const lower = fileName.toLowerCase();
    if (lower.includes("buyer") || lower.includes("bba") || lower.includes("builder")) {
      return "BUILDER_BUYER_AGREEMENT";
    }
    if (lower.includes("allotment")) return "ALLOTMENT_LETTER";
    if (lower.includes("sale") || lower.includes("agreement")) return "SALE_AGREEMENT";
    if (lower.includes("brochure") || lower.includes("spec")) return "PROJECT_BROCHURE";
    if (lower.includes("payment") || lower.includes("schedule")) return "PAYMENT_SCHEDULE";
    return "OTHER";
  };

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const newItems: SelectedFileItem[] = Array.from(files).map((file, idx) => ({
      id: `file-${Date.now()}-${idx}`,
      file,
      name: file.name,
      sizeFormatted: formatFileSize(file.size || 2500000),
      documentType: inferDocumentType(file.name),
      status: "READY",
    }));

    const updated = [...selectedFiles, ...newItems];
    setSelectedFiles(updated);
    if (onFilesChanged) onFilesChanged(updated);
  };

  const removeFile = (id: string) => {
    const updated = selectedFiles.filter((f) => f.id !== id);
    setSelectedFiles(updated);
    if (onFilesChanged) onFilesChanged(updated);
  };

  const updateType = (id: string, newType: DocumentType) => {
    const updated = selectedFiles.map((f) =>
      f.id === id ? { ...f, documentType: newType } : f
    );
    setSelectedFiles(updated);
    if (onFilesChanged) onFilesChanged(updated);
  };

  return (
    <div className={cn("space-y-4", className)}>
      {/* Drag & Drop Visual Box */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
        onClick={() => fileInputRef.current?.click()}
        className={cn(
          "border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 flex flex-col items-center justify-center",
          isDragging
            ? "border-emerald-500 bg-emerald-500/5 scale-[0.99]"
            : "border-surface-border bg-surface-subtle/50 hover:border-zinc-600 hover:bg-surface-subtle"
        )}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={(e) => handleFiles(e.target.files)}
          multiple
          accept=".pdf,.png,.jpg,.jpeg"
          className="hidden"
        />

        <div className="w-12 h-12 rounded-xl bg-zinc-800/80 border border-zinc-700/80 flex items-center justify-center text-zinc-300 mb-3 shadow-inner">
          <UploadCloud className="w-6 h-6 text-emerald-400" />
        </div>

        <h3 className="text-sm font-semibold text-zinc-100">
          Drop your transaction documents here
        </h3>
        <p className="text-xs text-zinc-400 mt-1 max-w-sm">
          Select or drag multiple PDFs belonging to this property transaction. ClauseGuard will analyze them together.
        </p>

        {/* Supported Document Tags */}
        <div className="flex flex-wrap items-center justify-center gap-1.5 mt-4">
          <span className="text-[10px] text-zinc-400 uppercase tracking-wider font-semibold mr-1">
            Supported:
          </span>
          {[
            "Builder-Buyer Agreement",
            "Sale Agreement",
            "Allotment Letter",
            "Payment Schedule",
            "Brochure",
          ].map((tag) => (
            <span
              key={tag}
              className="text-[10px] bg-zinc-800 text-zinc-300 px-2 py-0.5 rounded border border-zinc-700/80 font-mono"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>

      {/* Selected Files Staging List */}
      {selectedFiles.length > 0 && (
        <Card className="p-4">
          <div className="flex items-center justify-between mb-3 text-xs">
            <span className="font-semibold text-zinc-300">
              Selected Documents ({selectedFiles.length})
            </span>
            <span className="text-[11px] text-zinc-400">
              Tag document types accurately for cross-verification
            </span>
          </div>

          <div className="space-y-2.5">
            {selectedFiles.map((fileItem) => (
              <div
                key={fileItem.id}
                className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 rounded-lg bg-surface-subtle border border-surface-border text-xs"
              >
                {/* File info */}
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div className="w-8 h-8 rounded bg-zinc-800 border border-zinc-700 flex items-center justify-center text-zinc-400 flex-shrink-0">
                    <FileText className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="font-medium text-zinc-200 truncate">
                      {fileItem.name}
                    </p>
                    <span className="text-[10px] text-zinc-400 font-mono">
                      {fileItem.sizeFormatted} • Status: Ready
                    </span>
                  </div>
                </div>

                {/* Document Type Selector & Delete */}
                <div className="flex items-center gap-2">
                  <select
                    value={fileItem.documentType}
                    onChange={(e) =>
                      updateType(fileItem.id, e.target.value as DocumentType)
                    }
                    className="h-8 px-2.5 rounded bg-zinc-900 border border-zinc-700 text-xs text-zinc-200 focus:outline-none focus:border-emerald-500"
                  >
                    {DOCUMENT_TYPE_LABELS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>

                  <button
                    onClick={() => removeFile(fileItem.id)}
                    className="p-1.5 text-zinc-400 hover:text-rose-400 rounded hover:bg-zinc-800 transition-colors"
                    title="Remove file"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
