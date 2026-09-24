"use client";

import React from "react";
import { Sparkles } from "lucide-react";

interface SuggestedPromptBarProps {
  onSelectPrompt: (promptText: string) => void;
  prompts?: string[];
  disabled?: boolean;
}

const DEFAULT_PROMPTS = [
  "What happens if the builder delays handover beyond December 2027?",
  "What are my biggest risks in this transaction?",
  "Are there conflicting dates between the brochure and contract?",
  "What clauses should I negotiate before signing?",
  "What obligations do I have before taking possession?",
];

export const SuggestedPromptBar: React.FC<SuggestedPromptBarProps> = ({
  onSelectPrompt,
  prompts = DEFAULT_PROMPTS,
  disabled = false,
}) => {
  return (
    <div className="py-2.5">
      <div className="flex items-center gap-1.5 text-xs text-zinc-400 mb-2 font-medium">
        <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
        <span>Suggested Transaction Prompts:</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {prompts.map((p, idx) => (
          <button
            key={idx}
            type="button"
            disabled={disabled}
            onClick={() => onSelectPrompt(p)}
            className="text-left text-xs bg-zinc-900/80 hover:bg-zinc-800 text-zinc-300 hover:text-white px-3 py-1.5 rounded-lg border border-zinc-800 hover:border-zinc-700 transition-all active:scale-95 disabled:opacity-50"
          >
            {p}
          </button>
        ))}
      </div>
    </div>
  );
};
