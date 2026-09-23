"use client";

import React, { useState } from "react";
import {
  Sparkles,
  Search,
  Send,
  Loader2,
  FileText,
  AlertCircle,
  ShieldCheck,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Cpu,
  Layers,
  HelpCircle,
  RefreshCw,
  CheckCircle2,
  X,
} from "lucide-react";
import { RAGQueryResponse, RAGCitation } from "@/types/rag";
import { queryTransactionRAG } from "@/lib/api";
import { SourceEvidenceModal } from "./SourceEvidenceModal";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

interface SemanticExplorationWorkspaceProps {
  transactionId: string;
  isModal?: boolean;
  onClose?: () => void;
  autoFocusInput?: boolean;
}

const SUGGESTED_QUERIES = [
  "What is the penalty if the builder delays handover?",
  "What is the interest rate on delayed installment payment?",
  "What variation in carpet area is allowed without price adjustment?",
  "What is the earnest money forfeiture on buyer cancellation?",
  "Are there provisions for builder unilateral specification changes?",
];

export function SemanticExplorationWorkspace({
  transactionId,
  isModal = false,
  onClose,
  autoFocusInput = false,
}: SemanticExplorationWorkspaceProps) {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<RAGQueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedCitation, setSelectedCitation] = useState<RAGCitation | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [showAllEvidence, setShowAllEvidence] = useState(false);

  const handleSearch = async (questionToAsk?: string) => {
    const q = (questionToAsk || query).trim();
    if (!q || isLoading) return;

    if (questionToAsk) {
      setQuery(questionToAsk);
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await queryTransactionRAG(transactionId, q, 5);
      setResponse(data);
    } catch (err: any) {
      setError(err?.message || "Failed to retrieve grounded answers from transaction documents.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCitationClick = (citation: RAGCitation) => {
    setSelectedCitation(citation);
    setIsModalOpen(true);
  };

  return (
    <div
      id="ask-clauseguard-workspace"
      data-testid={isModal ? "rag-workspace-modal" : "rag-workspace"}
      className="space-y-6"
    >
      {/* Top Banner / Guidance */}
      <div className="p-4 rounded-xl bg-gradient-to-r from-emerald-950/30 via-surface-card to-purple-950/20 border border-emerald-500/20 shadow-subtle flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1 flex-1">
          <div className="flex items-center gap-2">
            <span className="p-1 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Sparkles className="w-4 h-4" />
            </span>
            <h2 className="text-sm font-bold text-white tracking-wide">
              Ask ClauseGuard — Grounded Document Intelligence
            </h2>
            <Badge variant="emerald" className="text-[10px] uppercase font-mono tracking-wider">
              Phase 8 RAG
            </Badge>
          </div>
          <p className="text-xs text-zinc-400 max-w-2xl leading-relaxed">
            Query across draft contracts, allotment letters, and payment schedules. Answers are generated
            strictly from retrieved document excerpts using 384-d FastEmbed embeddings and BM25 hybrid ranking.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-subtle border border-surface-border text-[11px] text-zinc-400">
            <Cpu className="w-3.5 h-3.5 text-emerald-400" />
            <span>100% Local Inference (384-d ONNX)</span>
          </div>
          {isModal && onClose && (
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors border border-surface-border"
              aria-label="Close modal"
              data-testid="rag-modal-close-btn"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Query Search Bar */}
      <Card className="p-2 sm:p-3 shadow-md border-surface-border">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch();
          }}
          className="flex items-center gap-2"
        >
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-zinc-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question about handover dates, penalty rates, carpet area, payment terms..."
              className="w-full bg-surface-base border border-surface-border rounded-lg pl-10 pr-4 py-2.5 text-xs sm:text-sm text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/30 transition-all font-sans"
              disabled={isLoading}
              autoFocus={autoFocusInput}
              data-testid="rag-query-input"
            />
          </div>
          <Button
            type="submit"
            variant="emerald"
            size="md"
            disabled={!query.trim() || isLoading}
            className="gap-2 text-xs sm:text-sm shrink-0 px-4"
            data-testid="rag-submit-btn"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="hidden sm:inline">Searching...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span className="hidden sm:inline">Ask ClauseGuard</span>
              </>
            )}
          </Button>
        </form>

        {/* Suggested Queries Chips */}
        <div className="mt-3 pt-3 border-t border-surface-border flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
          <span className="text-[11px] font-semibold text-zinc-400 shrink-0 flex items-center gap-1">
            <HelpCircle className="w-3 h-3 text-zinc-500" />
            Suggested:
          </span>
          {SUGGESTED_QUERIES.map((sq, idx) => (
            <button
              key={idx}
              onClick={() => handleSearch(sq)}
              disabled={isLoading}
              className="text-[11px] px-2.5 py-1 rounded-full bg-surface-subtle hover:bg-zinc-800 text-zinc-300 hover:text-white border border-surface-border hover:border-emerald-500/40 transition-all whitespace-nowrap"
            >
              {sq}
            </button>
          ))}
        </div>
      </Card>

      {/* Loading Skeleton */}
      {isLoading && (
        <Card className="p-6 space-y-4 border-emerald-500/30 bg-surface-card/60 animate-pulse">
          <div className="flex items-center gap-3">
            <Loader2 className="w-5 h-5 text-emerald-400 animate-spin" />
            <span className="text-xs font-medium text-emerald-400 font-mono">
              Running 384-dimensional dense semantic search & BM25 hybrid ranking...
            </span>
          </div>
          <div className="space-y-2">
            <div className="h-4 bg-zinc-800 rounded w-3/4"></div>
            <div className="h-4 bg-zinc-800 rounded w-5/6"></div>
            <div className="h-4 bg-zinc-800 rounded w-2/3"></div>
          </div>
          <div className="pt-2 flex gap-2">
            <div className="h-6 bg-zinc-800 rounded-full w-36"></div>
            <div className="h-6 bg-zinc-800 rounded-full w-48"></div>
          </div>
        </Card>
      )}

      {/* Error Message */}
      {error && !isLoading && (
        <Card className="p-4 border-rose-500/30 bg-rose-500/10 text-xs text-rose-300 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => handleSearch()}
            className="text-[11px] gap-1 shrink-0"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Retry</span>
          </Button>
        </Card>
      )}

      {/* Results View */}
      {response && !isLoading && (
        <div className="space-y-5 animate-in fade-in-50 duration-300">
          {/* State 1: Grounded Answer Found */}
          {response.grounded && response.status === "GROUNDED" ? (
            <Card className="p-6 border-emerald-500/30 bg-gradient-to-b from-surface-card to-surface-card/80 space-y-5 shadow-lg">
              {/* Answer Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-surface-border pb-4">
                <div className="flex items-center gap-2">
                  <Badge variant="emerald" className="gap-1.5 py-1 text-xs">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Grounded Transaction Answer</span>
                  </Badge>
                  <Badge variant="secondary" className="font-mono text-xs">
                    {Math.round(response.confidence * 100)}% Confidence
                  </Badge>
                </div>
                <div className="flex items-center gap-2 text-[11px] text-zinc-400">
                  <span className="font-mono">Engine: FastEmbed (384-d) + RRF</span>
                </div>
              </div>

              {/* Answer Narrative */}
              <div className="space-y-3 text-sm text-zinc-200 leading-relaxed">
                <div className="prose prose-invert prose-sm max-w-none">
                  {response.answer.split("\n\n").map((paragraph, idx) => {
                    if (paragraph.startsWith("> ")) {
                      return (
                        <blockquote
                          key={idx}
                          className="my-3 pl-4 border-l-2 border-emerald-500 text-zinc-300 italic bg-surface-subtle/50 py-2 pr-3 rounded-r-md"
                        >
                          {paragraph.replace(/^> /, "").replace(/"/g, "")}
                        </blockquote>
                      );
                    }
                    return (
                      <p key={idx} className="my-1.5">
                        {paragraph}
                      </p>
                    );
                  })}
                </div>
              </div>

              {/* Citation Chips */}
              <div className="space-y-2 pt-2 border-t border-surface-border">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] uppercase tracking-wider font-semibold text-zinc-400 flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-emerald-400" />
                    Contractual Citations ({response.citations.length})
                  </span>
                  <span className="text-[10px] text-zinc-500">
                    Click any citation to inspect verbatim text
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                  {response.citations.map((citation, idx) => (
                    <div
                      key={idx}
                      onClick={() => handleCitationClick(citation)}
                      className="p-3 rounded-lg bg-surface-subtle hover:bg-zinc-800/80 border border-surface-border hover:border-emerald-500/50 cursor-pointer transition-all space-y-2 group shadow-sm"
                    >
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold text-emerald-400 group-hover:text-emerald-300 font-mono text-[11px]">
                          {citation.clauseNumber || `Page ${citation.pageNumber}`}
                        </span>
                        <Badge variant="purple" className="text-[10px] px-1.5 py-0">
                          P.{citation.pageNumber}
                        </Badge>
                      </div>

                      <p className="text-xs text-zinc-200 font-medium truncate">
                        {citation.documentName}
                      </p>

                      <p className="text-[11px] text-zinc-400 line-clamp-2 italic font-mono bg-surface-base/60 p-1.5 rounded border border-surface-border/50">
                        "{citation.excerpt}"
                      </p>

                      <div className="flex items-center justify-between pt-1 text-[10px] text-zinc-500">
                        <span>Relevance: {Math.round(citation.relevanceScore * 100)}%</span>
                        <span className="text-emerald-400 group-hover:translate-x-0.5 transition-transform flex items-center gap-0.5">
                          Inspect <ExternalLink className="w-2.5 h-2.5" />
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Expandable All Evidence Section */}
              <div className="pt-2">
                <button
                  onClick={() => setShowAllEvidence(!showAllEvidence)}
                  className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-zinc-200 transition-colors"
                >
                  {showAllEvidence ? (
                    <>
                      <ChevronUp className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Hide Detailed Evidence Context</span>
                    </>
                  ) : (
                    <>
                      <ChevronDown className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Show Detailed Evidence Context ({response.citations.length} chunks)</span>
                    </>
                  )}
                </button>

                {showAllEvidence && (
                  <div className="mt-3 space-y-3 animate-in fade-in-50 duration-200">
                    {response.citations.map((c, i) => (
                      <div
                        key={i}
                        className="p-3.5 rounded-lg bg-surface-base border border-surface-border text-xs space-y-2"
                      >
                        <div className="flex items-center justify-between text-zinc-300 font-semibold">
                          <span>
                            {i + 1}. {c.documentName} — Page {c.pageNumber} ({c.clauseNumber || "Clause"})
                          </span>
                          <span className="font-mono text-emerald-400 text-[11px]">
                            RRF Match Score: {Math.round(c.relevanceScore * 100)}%
                          </span>
                        </div>
                        <p className="text-zinc-300 font-mono text-[11px] bg-zinc-900/60 p-2.5 rounded border border-zinc-800 leading-relaxed">
                          {c.excerpt}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Legal Disclaimer Footer */}
              <div className="pt-2 border-t border-surface-border/50 text-[11px] text-zinc-500">
                {response.disclaimer}
              </div>
            </Card>
          ) : (
            /* State 2: Insufficient Evidence / Anti-Hallucination Refusal */
            <Card className="p-6 border-amber-500/30 bg-amber-500/5 space-y-4">
              <div className="flex items-center gap-2">
                <Badge variant="amber" className="gap-1 py-1 text-xs">
                  <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
                  <span>Statutory Anti-Hallucination Guardrail Active</span>
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Insufficient Evidence
                </Badge>
              </div>

              <div className="space-y-2">
                <h3 className="text-base font-bold text-zinc-100">
                  No Grounded Contractual Evidence Found
                </h3>
                <p className="text-xs text-zinc-300 leading-relaxed bg-surface-card p-4 rounded-lg border border-amber-500/20">
                  {response.answer}
                </p>
              </div>

              <div className="p-3.5 rounded-lg bg-surface-subtle border border-surface-border text-xs text-zinc-400 space-y-1">
                <span className="font-semibold text-zinc-300 block">
                  Why did ClauseGuard refuse to speculate?
                </span>
                <p className="text-[11px] leading-relaxed">
                  Unlike consumer chatbots that guess or hallucinate plausible terms, ClauseGuard enforces
                  strict contractual lineage. If a provision (e.g. amenities, specific fixtures, interior finishes)
                  is missing from the uploaded documents, we explicitly alert you so you can request the relevant
                  annexure directly from the developer.
                </p>
              </div>
            </Card>
          )}
        </div>
      )}

      {/* Empty / Initial State */}
      {!response && !isLoading && !error && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          <Card className="p-4 space-y-2 border-surface-border bg-surface-card/60">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 w-fit">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <h3 className="text-xs font-bold text-white">Strict Legal Grounding</h3>
            <p className="text-[11px] text-zinc-400 leading-relaxed">
              Every answer is grounded exclusively in uploaded contracts. The engine never hallucinates or invents terms.
            </p>
          </Card>

          <Card className="p-4 space-y-2 border-surface-border bg-surface-card/60">
            <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400 w-fit">
              <Layers className="w-4 h-4" />
            </div>
            <h3 className="text-xs font-bold text-white">Full Provenance Lineage</h3>
            <p className="text-[11px] text-zinc-400 leading-relaxed">
              Each response provides clickable citation chips linking directly to the exact Document, Page, and Clause.
            </p>
          </Card>

          <Card className="p-4 space-y-2 border-surface-border bg-surface-card/60">
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 w-fit">
              <Cpu className="w-4 h-4" />
            </div>
            <h3 className="text-xs font-bold text-white">100% Offline & Local</h3>
            <p className="text-[11px] text-zinc-400 leading-relaxed">
              Powered by local FastEmbed 384-dimensional ONNX embeddings and SQLite. Zero external API calls.
            </p>
          </Card>
        </div>
      )}

      {/* Citation Inspector Modal */}
      <SourceEvidenceModal
        citation={selectedCitation}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        transactionId={transactionId}
      />
    </div>
  );
}
