import React from "react";
import Link from "next/link";
import {
  Shield,
  ArrowRight,
  FileText,
  Split,
  AlertTriangle,
  CalendarCheck,
  CheckCircle2,
  Layers,
  Sparkles,
  Search,
  ExternalLink,
  ShieldAlert,
} from "lucide-react";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { SeverityBadge } from "@/components/shared/SeverityBadge";
import { LegalDisclaimerNotice } from "@/components/shared/LegalDisclaimerNotice";

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground">
      <Navbar />

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-20 pb-24 md:pt-28 md:pb-32 border-b border-surface-border">
        {/* Subtle background glow */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-emerald-500/10 blur-[130px] rounded-full pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface-subtle border border-surface-border text-xs text-zinc-300 mb-6">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-medium">
              Cross-Document Intelligence Platform
            </span>
            <span className="text-zinc-500">•</span>
            <span className="text-emerald-400">Transaction Copilot Active</span>
          </div>

          {/* Heading & Tagline */}
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-[1.1]">
            Understand your property documents{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-300 to-emerald-500">
              before you sign.
            </span>
          </h1>

          <p className="mt-6 text-base sm:text-lg text-zinc-400 max-w-2xl mx-auto leading-relaxed">
            ClauseGuard analyzes your Builder-Buyer Agreement, Sale Agreement, Allotment Letter, Payment Schedule, and Marketing Brochure together to detect hidden risks and cross-document inconsistencies.
          </p>

          {/* CTAs */}
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/dashboard/transactions/new">
              <Button variant="emerald" size="lg" className="w-full sm:w-auto gap-2 shadow-subtle-glow">
                <span>Analyze a Transaction</span>
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>

            <a href="#how-it-works">
              <Button variant="secondary" size="lg" className="w-full sm:w-auto">
                See How It Works
              </Button>
            </a>

            <Link href="/dashboard/transactions/skyview-a1204">
              <Button variant="outline" size="lg" className="w-full sm:w-auto text-zinc-300">
                Explore Demo Bundle
              </Button>
            </Link>
          </div>

          {/* Informational Disclaimer under Hero */}
          <div className="mt-6 max-w-md mx-auto">
            <LegalDisclaimerNotice variant="compact" />
          </div>

          {/* VISUAL REPRESENTATION: Multi-Document Ingestion Flow Diagram */}
          <div className="mt-16 max-w-5xl mx-auto">
            <div className="rounded-2xl border border-surface-border bg-surface/70 backdrop-blur-md p-6 sm:p-8 shadow-2xl relative">
              <div className="text-xs uppercase tracking-wider font-semibold text-zinc-400 mb-6 flex items-center justify-between">
                <span>Multi-Document Cross-Verification Pipeline</span>
                <span className="font-mono text-emerald-400 text-[11px]">
                  Unified Transaction Model
                </span>
              </div>

              {/* Graphic Flow: Documents -> Core Engine -> Cross-Findings */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
                {/* 1. Ingested Bundle Documents */}
                <div className="space-y-2.5">
                  <div className="text-left text-[11px] font-semibold text-zinc-400 uppercase tracking-wider mb-2">
                    Transaction Bundle (4 Files)
                  </div>
                  {[
                    { name: "Project Brochure", meta: "1,450 sq.ft advertised", color: "text-blue-400" },
                    { name: "Signed Allotment Letter", meta: "30 June 2027 delivery", color: "text-purple-400" },
                    { name: "Builder-Buyer Agreement", meta: "1,380 sq.ft legal area", color: "text-amber-400" },
                    { name: "Payment Schedule", meta: "10 milestones, ₹1.42 Cr", color: "text-emerald-400" },
                  ].map((doc, i) => (
                    <div
                      key={i}
                      className="p-3 rounded-lg bg-surface-subtle border border-surface-border text-left flex items-center justify-between text-xs"
                    >
                      <div className="flex items-center gap-2.5 truncate">
                        <FileText className={`w-4 h-4 ${doc.color} flex-shrink-0`} />
                        <span className="font-medium text-zinc-200 truncate">{doc.name}</span>
                      </div>
                      <span className="text-[10px] text-zinc-400 font-mono flex-shrink-0 ml-2">
                        {doc.meta}
                      </span>
                    </div>
                  ))}
                </div>

                {/* 2. ClauseGuard Central Processing Hub */}
                <div className="flex flex-col items-center justify-center p-6 rounded-xl bg-zinc-900 border border-emerald-500/30 shadow-subtle-glow">
                  <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/40 flex items-center justify-center text-emerald-400 mb-3">
                    <Shield className="w-6 h-6" />
                  </div>
                  <span className="text-xs font-bold text-white uppercase tracking-wider">
                    ClauseGuard Engine
                  </span>
                  <span className="text-[11px] text-zinc-400 text-center mt-1">
                    Deterministic Discrepancy Matrix & Semantic Verification
                  </span>
                  <div className="mt-3 inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-mono">
                    <Sparkles className="w-3 h-3" />
                    <span>Cross-Document Alignment</span>
                  </div>
                </div>

                {/* 3. Output Finding Card Preview */}
                <div className="space-y-3">
                  <div className="text-left text-[11px] font-semibold text-zinc-400 uppercase tracking-wider mb-2">
                    Evidence-Backed Finding
                  </div>
                  <div className="p-4 rounded-xl bg-purple-950/20 border border-purple-500/40 text-left space-y-2">
                    <div className="flex items-center justify-between">
                      <SeverityBadge type="POTENTIAL_INCONSISTENCY" size="sm" />
                      <span className="font-mono text-[10px] text-purple-400">
                        70 sq.ft Mismatch
                      </span>
                    </div>
                    <p className="text-xs font-semibold text-zinc-100">
                      Carpet Area Discrepancy Detected
                    </p>
                    <div className="space-y-1.5 text-[11px]">
                      <div className="flex justify-between text-zinc-400">
                        <span>Brochure (Pg 4):</span>
                        <span className="font-mono text-zinc-200">1,450 sq.ft</span>
                      </div>
                      <div className="flex justify-between text-purple-300">
                        <span>Agreement (Cl 4.1):</span>
                        <span className="font-mono font-bold text-purple-200">1,380 sq.ft</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Section 2: Core Value Pillars */}
      <section id="intelligence" className="py-20 border-b border-surface-border bg-surface/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="text-xs uppercase font-semibold text-emerald-400 tracking-wider">
              Beyond Simple PDF Summaries
            </span>
            <h2 className="text-2xl sm:text-4xl font-bold text-white mt-2 tracking-tight">
              True Cross-Document Transaction Intelligence
            </h2>
            <p className="text-sm text-zinc-400 mt-3 leading-relaxed">
              Real-estate developers provide scattered documents over months. ClauseGuard connects the dots to protect your financial and legal interests.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Pillar 1: Understand Documents */}
            <Card className="p-6 hover:border-zinc-700 transition-all">
              <div className="w-10 h-10 rounded-lg bg-surface-subtle border border-surface-border flex items-center justify-center text-emerald-400 mb-4">
                <FileText className="w-5 h-5" />
              </div>
              <h3 className="text-base font-semibold text-zinc-100 mb-2">
                Understand Your Documents
              </h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Translate opaque legalese into clear, plain-language insights. Parse dense clauses on handover, defects liability, and building plan approvals with complete clarity.
              </p>
            </Card>

            {/* Pillar 2: Detect Potential Risks */}
            <Card className="p-6 hover:border-zinc-700 transition-all">
              <div className="w-10 h-10 rounded-lg bg-surface-subtle border border-surface-border flex items-center justify-center text-rose-400 mb-4">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <h3 className="text-base font-semibold text-zinc-100 mb-2">
                Detect Potential Risks
              </h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Highlight asymmetrical penalty terms (e.g., Buyer pays 18% p.a. for late payments while developer pays ₹5/sq.ft/month for delayed delivery), aggressive forfeiture clauses, and unilateral alteration waivers.
              </p>
            </Card>

            {/* Pillar 3: Find Inconsistencies */}
            <Card className="p-6 hover:border-zinc-700 transition-all">
              <div className="w-10 h-10 rounded-lg bg-surface-subtle border border-surface-border flex items-center justify-center text-purple-400 mb-4">
                <Split className="w-5 h-5" />
              </div>
              <h3 className="text-base font-semibold text-zinc-100 mb-2">
                Find Inconsistencies
              </h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Catch conflicting terms across documents. Detect when carpet areas shrink from marketing flyers to legal deeds, or when promised possession dates quietly slide back in agreement drafts.
              </p>
            </Card>

            {/* Pillar 4: Track Obligations */}
            <Card className="p-6 hover:border-zinc-700 transition-all">
              <div className="w-10 h-10 rounded-lg bg-surface-subtle border border-surface-border flex items-center justify-center text-blue-400 mb-4">
                <CalendarCheck className="w-5 h-5" />
              </div>
              <h3 className="text-base font-semibold text-zinc-100 mb-2">
                Track Critical Obligations
              </h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Maintain a crystal-clear cash-flow timeline. Map payment schedule installments directly against construction milestones, statutory due dates, and grace periods.
              </p>
            </Card>

            {/* Pillar 5: Evidence-Backed Insights */}
            <Card className="p-6 hover:border-zinc-700 transition-all md:col-span-2">
              <div className="w-10 h-10 rounded-lg bg-surface-subtle border border-surface-border flex items-center justify-center text-emerald-400 mb-4">
                <Shield className="w-5 h-5" />
              </div>
              <h3 className="text-base font-semibold text-zinc-100 mb-2">
                Get Evidence-Backed Insights (Zero Hallucination)
              </h3>
              <p className="text-xs text-zinc-400 leading-relaxed max-w-2xl">
                Every single finding is rigorously anchored to its source: <strong>Document &rarr; Page &rarr; Clause &rarr; Exact Raw Excerpt</strong>. Inspect the original clause directly in our synchronized split-pane document viewer with one click.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* Section 3: Interactive Real-World Discrepancy Spotlight */}
      <section id="discrepancies" className="py-20 border-b border-surface-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12">
            <div>
              <span className="text-xs uppercase font-semibold text-purple-400 tracking-wider">
                Cross-Document Intelligence in Action
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold text-white mt-1">
                How ClauseGuard Uncovers Planted Contradictions
              </h2>
            </div>
            <Link href="/dashboard/transactions/skyview-a1204">
              <Button variant="outline" size="sm" className="mt-4 md:mt-0 gap-1.5 text-zinc-300">
                <span>View Full SkyView Report</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Button>
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Example 1: Area Mismatch */}
            <Card className="p-6 border-l-4 border-l-purple-500">
              <div className="flex items-center justify-between mb-3">
                <SeverityBadge type="POTENTIAL_INCONSISTENCY" />
                <span className="text-xs text-zinc-400 font-mono">Area Metric Discrepancy</span>
              </div>
              <h3 className="text-sm font-semibold text-zinc-100 mb-2">
                Carpet Area Reduction Between Brochure & Agreement
              </h3>
              <p className="text-xs text-zinc-400 mb-4 leading-relaxed">
                The marketing brochure heavily promotes an expansive 1,450 sq.ft carpet area, while Clause 4.1 of the formal sale agreement reduces legal carpet area to 1,380 sq.ft, reserving a further &plusmn;3% variation right.
              </p>
              <div className="space-y-2 text-xs">
                <div className="p-2.5 rounded bg-surface-subtle border border-surface-border">
                  <span className="text-[10px] text-zinc-400 uppercase font-semibold block">
                    Brochure (Page 4):
                  </span>
                  <span className="italic text-zinc-200">
                    &ldquo;1450 sq.ft (134.7 sq.m) elite 3BHK carpet area with sundeck.&rdquo;
                  </span>
                </div>
                <div className="p-2.5 rounded bg-purple-950/20 border border-purple-500/30">
                  <span className="text-[10px] text-purple-400 uppercase font-semibold block">
                    Sale Agreement (Page 12, Clause 4.1):
                  </span>
                  <span className="italic text-purple-200">
                    &ldquo;RERA Carpet Area of 1,380 sq. ft. ... Promoter reserves right to make up to &plusmn;3% variation.&rdquo;
                  </span>
                </div>
              </div>
            </Card>

            {/* Example 2: Possession Timeline Discrepancy */}
            <Card className="p-6 border-l-4 border-l-amber-500">
              <div className="flex items-center justify-between mb-3">
                <SeverityBadge type="MEDIUM" label="Possession Timeline Shift" />
                <span className="text-xs text-zinc-400 font-mono">Timeline Discrepancy</span>
              </div>
              <h3 className="text-sm font-semibold text-zinc-100 mb-2">
                Delivery Date Postponement & Added Grace Window
              </h3>
              <p className="text-xs text-zinc-400 mb-4 leading-relaxed">
                The signed allotment letter promises key handover by 30 June 2027. However, the Builder-Buyer Agreement postpones scheduled completion to 31 December 2027 and adds an unconditional 180-day grace period.
              </p>
              <div className="space-y-2 text-xs">
                <div className="p-2.5 rounded bg-surface-subtle border border-surface-border">
                  <span className="text-[10px] text-zinc-400 uppercase font-semibold block">
                    Allotment Letter (Page 2):
                  </span>
                  <span className="italic text-zinc-200">
                    &ldquo;Target possession and handover ... projected for 30th June 2027.&rdquo;
                  </span>
                </div>
                <div className="p-2.5 rounded bg-amber-950/20 border border-amber-500/30">
                  <span className="text-[10px] text-amber-300">
                    Sale Agreement (Page 19, Clause 11.2):
                  </span>
                  <span className="italic text-amber-200 block">
                    &ldquo;Proposes to complete construction by 31st December 2027 ... entitled to an unconditional grace period of 180 days.&rdquo;
                  </span>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* Section 4: How It Works */}
      <section id="how-it-works" className="py-20 border-b border-surface-border bg-surface/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <span className="text-xs uppercase font-semibold text-emerald-400 tracking-wider">
              Step-by-Step Methodology
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold text-white mt-1">
              How ClauseGuard Analyzes a Transaction
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                step: "01",
                title: "Upload Transaction Bundle",
                desc: "Drop all documents for your property deal: BBA, Allotment Letter, Payment Schedule, and Brochure.",
              },
              {
                step: "02",
                title: "Extract & Tag Clauses",
                desc: "High-speed text parsing with OCR fallback segments contracts into distinct numbered articles and legal clauses.",
              },
              {
                step: "03",
                title: "Cross-Document Matrix",
                desc: "The intelligence engine correlates key figures (Area, Price, Timeline) across documents to locate discrepancies.",
              },
              {
                step: "04",
                title: "Evidence-Backed Report",
                desc: "Inspect findings in our split-view workspace. Every risk is linked directly to exact contract page coordinates.",
              },
            ].map((s, idx) => (
              <div key={idx} className="relative p-6 rounded-xl bg-surface border border-surface-border">
                <span className="text-3xl font-black font-mono text-zinc-700 block mb-3">
                  {s.step}
                </span>
                <h3 className="text-sm font-semibold text-zinc-100 mb-2">
                  {s.title}
                </h3>
                <p className="text-xs text-zinc-400 leading-relaxed">
                  {s.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Bottom CTA Banner */}
      <section className="py-20 relative overflow-hidden text-center">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 space-y-6">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Ready to review your real-estate transaction?
          </h2>
          <p className="text-sm text-zinc-400 max-w-xl mx-auto leading-relaxed">
            Get an instant cross-document intelligence report on your property documents before signing any binding commitment.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
            <Link href="/dashboard/transactions/new">
              <Button variant="emerald" size="lg" className="gap-2">
                <span>Start New Transaction</span>
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="outline" size="lg">
                Go to Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
