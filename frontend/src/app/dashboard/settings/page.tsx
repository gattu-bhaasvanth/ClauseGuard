"use client";

import React, { useState } from "react";
import { Settings, Shield, Sliders, Database, Cpu } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export default function SettingsPage() {
  const [provider, setProvider] = useState("gemini");
  const [ocrEngine, setOcrEngine] = useState("paddleocr");

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="pb-4 border-b border-surface-border">
        <h1 className="text-2xl font-bold tracking-tight text-white">
          System & Engine Configuration
        </h1>
        <p className="text-xs text-zinc-400 mt-1">
          Frontend preferences and preview of backend AI/OCR provider integrations
        </p>
      </div>

      {/* LLM Provider Configuration Preview */}
      <Card className="p-6 space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b border-surface-border">
          <Cpu className="w-4 h-4 text-emerald-400" />
          <h2 className="text-sm font-semibold text-zinc-100">
            LLM Provider Layer (Phase 2 & 8)
          </h2>
        </div>

        <p className="text-xs text-zinc-400 leading-relaxed">
          ClauseGuard utilizes a modular provider architecture allowing you to swap model backends seamlessly.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          {[
            { id: "gemini", name: "Google Gemini 1.5", tag: "Recommended", desc: "Long-context document reasoning" },
            { id: "openai", name: "OpenAI GPT-4o", tag: "Supported", desc: "General clause extraction" },
            { id: "anthropic", name: "Anthropic Claude 3.5", tag: "Supported", desc: "High legal-text nuance" },
          ].map((item) => (
            <div
              key={item.id}
              onClick={() => setProvider(item.id)}
              className={`p-3.5 rounded-lg border cursor-pointer transition-all ${
                provider === item.id
                  ? "border-emerald-500 bg-emerald-500/10 text-white shadow-sm"
                  : "border-surface-border bg-surface-subtle text-zinc-400 hover:border-zinc-700"
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-zinc-200">{item.name}</span>
                <span className="text-[10px] text-emerald-400 font-mono">{item.tag}</span>
              </div>
              <p className="text-[11px] text-zinc-500">{item.desc}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* OCR Engine Settings Preview */}
      <Card className="p-6 space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b border-surface-border">
          <Sliders className="w-4 h-4 text-emerald-400" />
          <h2 className="text-sm font-semibold text-zinc-100">
            Document Ingestion & OCR Fallback (Phase 3)
          </h2>
        </div>

        <div className="space-y-3 text-xs">
          <div className="flex items-center justify-between p-3 rounded-lg bg-surface-subtle border border-surface-border">
            <div>
              <span className="font-medium text-zinc-200 block">
                Primary Extraction: PyMuPDF (fitz)
              </span>
              <span className="text-[11px] text-zinc-500">
                Direct character extraction with exact bounding boxes for digital PDFs
              </span>
            </div>
            <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded font-mono">
              Active
            </span>
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg bg-surface-subtle border border-surface-border">
            <div>
              <span className="font-medium text-zinc-200 block">
                OCR Fallback Engine: PaddleOCR
              </span>
              <span className="text-[11px] text-zinc-500">
                Triggered automatically on scanned pages or stamped legal paper
              </span>
            </div>
            <span className="text-[10px] bg-zinc-800 text-zinc-300 border border-zinc-700 px-2 py-0.5 rounded font-mono">
              Configured
            </span>
          </div>
        </div>
      </Card>
    </div>
  );
}
