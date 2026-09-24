"use client";

import React, { useState } from "react";
import { Copy, Check, MessageSquareCode } from "lucide-react";

interface NegotiationScriptBoxProps {
  script: string;
}

export const NegotiationScriptBox: React.FC<NegotiationScriptBoxProps> = ({
  script,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(script);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="p-4 rounded-xl bg-zinc-900/90 border border-zinc-800">
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-zinc-300">
          <MessageSquareCode className="w-4 h-4 text-emerald-400" />
          <span>Recommended Builder Amendment Language:</span>
        </div>
        <button
          onClick={handleCopy}
          className="inline-flex items-center gap-1.5 text-xs text-zinc-400 hover:text-emerald-400 transition-colors px-2 py-1 rounded bg-zinc-800/80 hover:bg-zinc-800 border border-zinc-700/60"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-emerald-400">Copied</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span>Copy Language</span>
            </>
          )}
        </button>
      </div>

      <div className="p-3 rounded-lg bg-zinc-950/80 border border-zinc-800/80 text-xs font-mono text-zinc-300 leading-relaxed whitespace-pre-wrap select-all">
        {script}
      </div>
      <p className="text-[11px] text-zinc-400 mt-2">
        Submit this specific draft rider clause to the developer or your conveyance attorney to request pre-signing revision.
      </p>
    </div>
  );
};
