"use client";

import React from "react";
import { CopilotChatMessage, CopilotCitation } from "@/types/copilot";
import { ShieldCheck, AlertCircle, FileText, Sparkles, User } from "lucide-react";

interface CopilotMessageListProps {
  messages: CopilotChatMessage[];
  onSelectCitation?: (citation: CopilotCitation) => void;
  onSelectSuggestedPrompt?: (prompt: string) => void;
}

export const CopilotMessageList: React.FC<CopilotMessageListProps> = ({
  messages,
  onSelectCitation,
  onSelectSuggestedPrompt,
}) => {
  return (
    <div className="space-y-4">
      {messages.map((m) => {
        const isUser = m.role === "user";

        if (isUser) {
          return (
            <div key={m.id} className="flex justify-end">
              <div className="max-w-[85%] rounded-2xl bg-zinc-800/90 border border-zinc-700/80 px-4 py-3 text-sm text-zinc-100 shadow-md">
                <div className="flex items-center gap-1.5 text-[10px] font-mono text-zinc-400 mb-1 justify-end">
                  <User className="w-3 h-3 text-zinc-400" />
                  <span>{m.timestamp}</span>
                </div>
                <p className="whitespace-pre-wrap">{m.content}</p>
              </div>
            </div>
          );
        }

        return (
          <div key={m.id} className="flex justify-start">
            <div className="max-w-[92%] rounded-2xl bg-[#111622] border border-zinc-800 p-4 text-sm text-zinc-200 shadow-lg">
              {/* Header */}
              <div className="flex flex-wrap items-center justify-between gap-2 pb-2.5 mb-3 border-b border-zinc-800/80 text-xs">
                <div className="flex items-center gap-2">
                  <div className="p-1 rounded bg-emerald-500/10 border border-emerald-500/20">
                    <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                  </div>
                  <span className="font-semibold text-zinc-100">ClauseGuard Copilot</span>
                  {m.intent && (
                    <span className="font-mono text-[10px] bg-zinc-800 text-zinc-400 px-2 py-0.5 rounded border border-zinc-700/60">
                      {m.intent}
                    </span>
                  )}
                </div>

                {m.refused ? (
                  <span className="flex items-center gap-1 text-[11px] font-medium text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                    <AlertCircle className="w-3 h-3" />
                    <span>Evidence Refusal</span>
                  </span>
                ) : m.grounded ? (
                  <span className="flex items-center gap-1 text-[11px] font-medium text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                    <ShieldCheck className="w-3 h-3" />
                    <span>Grounded in Evidence</span>
                  </span>
                ) : null}
              </div>

              {/* Main Content */}
              <div className="prose prose-invert prose-sm max-w-none text-zinc-300 leading-relaxed space-y-2 whitespace-pre-wrap">
                {m.content}
              </div>

              {/* Citations Section */}
              {m.citations && m.citations.length > 0 && (
                <div className="mt-4 pt-3 border-t border-zinc-800/80">
                  <div className="text-[11px] uppercase tracking-wider font-mono text-zinc-400 mb-2 flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Source Evidence Citations ({m.citations.length}):</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {m.citations.map((c, cIdx) => (
                      <button
                        key={cIdx}
                        onClick={() => onSelectCitation?.(c)}
                        className="text-left text-xs bg-zinc-900/90 hover:bg-zinc-800 border border-emerald-500/30 hover:border-emerald-400/60 text-zinc-200 px-2.5 py-1.5 rounded-lg transition-all active:scale-95 group flex items-center gap-1.5"
                      >
                        <span className="font-mono text-[10px] text-emerald-400">
                          {c.clauseNumber || `Page ${c.pageNumber}`}
                        </span>
                        <span className="text-zinc-400 text-[11px] truncate max-w-[180px]">
                          {c.documentName}
                        </span>
                        <span className="text-emerald-400 opacity-60 group-hover:opacity-100">
                          ↗
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Suggested Follow-up Questions */}
              {m.suggestedNextQuestions && m.suggestedNextQuestions.length > 0 && (
                <div className="mt-3.5 pt-2.5 border-t border-zinc-800/60 flex flex-wrap gap-1.5 items-center">
                  <span className="text-[10px] text-zinc-400 font-mono">Suggested follow-up:</span>
                  {m.suggestedNextQuestions.map((q, qIdx) => (
                    <button
                      key={qIdx}
                      onClick={() => onSelectSuggestedPrompt?.(q)}
                      className="text-[11px] bg-zinc-900/70 hover:bg-zinc-800 text-zinc-400 hover:text-emerald-300 px-2.5 py-1 rounded border border-zinc-800 hover:border-emerald-500/30 transition-colors"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
