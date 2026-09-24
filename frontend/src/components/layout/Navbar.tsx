"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Shield, ArrowRight, Menu, X } from "lucide-react";
import { Button } from "@/components/ui/Button";

export function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-surface-border/60 bg-background/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 group-hover:border-emerald-500/60 transition-colors">
            <Shield className="w-4 h-4" />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-base tracking-tight text-white">
                ClauseGuard
              </span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface-subtle border border-surface-border text-emerald-400">
                v1.0
              </span>
            </div>
            <span className="text-[10px] text-zinc-400 hidden sm:inline-block">
              Real-Estate Transaction Intelligence
            </span>
          </div>
        </Link>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center gap-8 text-xs font-medium text-zinc-400">
          <a
            href="#intelligence"
            className="hover:text-zinc-100 transition-colors"
          >
            Capabilities
          </a>
          <a
            href="#how-it-works"
            className="hover:text-zinc-100 transition-colors"
          >
            How It Works
          </a>
          <a
            href="#discrepancies"
            className="hover:text-zinc-100 transition-colors"
          >
            Cross-Doc Intelligence
          </a>
          <Link
            href="/dashboard/transactions/skyview-a1204"
            className="text-emerald-400 hover:text-emerald-300 transition-colors"
          >
            Live Demo
          </Link>
        </nav>

        {/* Action Buttons */}
        <div className="hidden sm:flex items-center gap-3">
          <Link href="/dashboard">
            <Button variant="outline" size="sm">
              Dashboard
            </Button>
          </Link>
          <Link href="/dashboard/transactions/new">
            <Button variant="emerald" size="sm" className="gap-1.5">
              <span>Start Analysis</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Button>
          </Link>
        </div>

        {/* Mobile Hamburger Toggle */}
        <div className="flex md:hidden">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 text-zinc-400 hover:text-white"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-surface-border bg-background px-4 py-4 space-y-3">
          <nav className="flex flex-col space-y-2 text-sm text-zinc-300">
            <a
              href="#intelligence"
              onClick={() => setMobileMenuOpen(false)}
              className="py-1 hover:text-white"
            >
              Capabilities
            </a>
            <a
              href="#how-it-works"
              onClick={() => setMobileMenuOpen(false)}
              className="py-1 hover:text-white"
            >
              How It Works
            </a>
            <a
              href="#discrepancies"
              onClick={() => setMobileMenuOpen(false)}
              className="py-1 hover:text-white"
            >
              Cross-Doc Intelligence
            </a>
            <Link
              href="/dashboard/transactions/skyview-a1204"
              onClick={() => setMobileMenuOpen(false)}
              className="py-1 text-emerald-400"
            >
              Live Demo (SkyView)
            </Link>
          </nav>
          <div className="pt-2 flex flex-col gap-2">
            <Link href="/dashboard">
              <Button variant="outline" size="sm" className="w-full">
                View Dashboard
              </Button>
            </Link>
            <Link href="/dashboard/transactions/new">
              <Button variant="emerald" size="sm" className="w-full">
                Analyze a Transaction
              </Button>
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
