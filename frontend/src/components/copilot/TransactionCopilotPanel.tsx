"use client";

import React, { useState, useEffect, useRef } from "react";
import { CopilotChatMessage, CopilotCitation } from "@/types/copilot";
import { CopilotMessageList } from "./CopilotMessageList";
import { SuggestedPromptBar } from "./SuggestedPromptBar";
import { queryCopilot } from "@/lib/api";
import { X, Send, Sparkles, Loader2, Bot, Shield } from "lucide-react";

interface TransactionCopilotPanelProps {
  isOpen: boolean;
  onClose: () => void;
  bundleId: string;
  onSelectCitation?: (citation: CopilotCitation) => void;
}

export const TransactionCopilotPanel: React.FC<TransactionCopilotPanelProps> = ({
  isOpen,
  onClose,
  bundleId,
  onSelectCitation,
}) => {
  const [messages, setMessages] = useState<CopilotChatMessage[]>([
    {
      id: "msg-welcome",
      role: "assistant",
      content:
        "Welcome to the **ClauseGuard Transaction Copilot**. I am trained to reason across your entire uploaded transaction bundle with 100% grounded evidence.\n\nAsk me about contractual risks, delay penalties, carpet area measurements, payment milestones, or conflicting dates.",
      timestamp: "Just now",
      intent: "WELCOME",
      grounded: true,
      refused: false,
      suggestedNextQuestions: [
        "What happens if the builder delays handover beyond December 2027?",
        "What are my biggest risks in this transaction?",
        "Are there conflicting dates between the brochure and contract?",
      ],
    },
  ]);
  const [inputQuery, setInputQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const inputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen]);

  // Global Escape key listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  // Auto-scroll on new message
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSubmit = async (queryText?: string) => {
    const q = (queryText !== undefined ? queryText : inputQuery).trim();
    if (!q || isLoading) return;

    const userMsg: CopilotChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: q,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery("");
    setIsLoading(true);

    try {
      const response = await queryCopilot(bundleId, q);

      const botMsg: CopilotChatMessage = {
        id: `bot-${Date.now()}`,
        role: "assistant",
        content: response.answer,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        intent: response.intent,
        grounded: response.grounded,
        refused: response.refused,
        confidence: response.confidence,
        citations: response.citations,
        suggestedNextQuestions: response.suggestedNextQuestions,
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      const errorMsg: CopilotChatMessage = {
        id: `bot-err-${Date.now()}`,
        role: "assistant",
        content: "An error occurred while evaluating your question. Please verify your query and try again.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        grounded: false,
        refused: true,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm transition-opacity duration-300"
      role="dialog"
      aria-modal="true"
      aria-label="Transaction Copilot"
    >
      <div className="w-full max-w-2xl bg-[#0b0e14] border-l border-zinc-800 h-full flex flex-col shadow-2xl animate-in slide-in-from-right duration-300">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-zinc-800 bg-[#10141d]">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
              <Bot className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-semibold text-zinc-100">
                  Transaction Copilot
                </h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Grounded Mode
                </span>
              </div>
              <p className="text-xs text-zinc-400">
                Multi-document synthesis & statutory verification for {bundleId}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <kbd className="hidden sm:inline-block text-[10px] text-zinc-400 bg-zinc-800 px-2 py-1 rounded border border-zinc-700 font-mono">
              ESC
            </kbd>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors"
              aria-label="Close Copilot"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Messages Body */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
          <CopilotMessageList
            messages={messages}
            onSelectCitation={onSelectCitation}
            onSelectSuggestedPrompt={(p) => handleSubmit(p)}
          />

          {isLoading && (
            <div className="flex justify-start">
              <div className="max-w-[80%] rounded-2xl bg-[#111622] border border-zinc-800 p-4 text-xs text-zinc-400 flex items-center gap-3">
                <Loader2 className="w-4 h-4 text-emerald-400 animate-spin" />
                <span>Scanning document chunks & synthesizing grounded citations...</span>
              </div>
            </div>
          )}
        </div>

        {/* Footer Input Area */}
        <div className="p-4 border-t border-zinc-800 bg-[#0e121a]">
          <SuggestedPromptBar
            onSelectPrompt={(p) => handleSubmit(p)}
            disabled={isLoading}
          />

          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSubmit();
            }}
            className="flex items-center gap-2 mt-2"
          >
            <input
              ref={inputRef}
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              placeholder="Ask a question about this property transaction..."
              disabled={isLoading}
              className="flex-1 bg-zinc-900 border border-zinc-700/80 rounded-xl px-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 disabled:opacity-50 transition-colors"
            />
            <button
              type="submit"
              disabled={!inputQuery.trim() || isLoading}
              className="px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-zinc-950 font-semibold text-sm transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              <span className="hidden sm:inline">Ask</span>
            </button>
          </form>

          <div className="mt-2 flex items-center justify-between text-[11px] text-zinc-400">
            <span className="flex items-center gap-1 text-emerald-400">
              <Shield className="w-3 h-3" />
              100% Offline FastEmbed Embeddings
            </span>
            <span>Press Enter to send</span>
          </div>
        </div>
      </div>
    </div>
  );
};
