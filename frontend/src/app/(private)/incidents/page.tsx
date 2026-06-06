"use client";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import Image from "next/image";
import { analyzeIncident } from "@/lib/api";
import { AlertTriangle, Loader2, Wrench, Laugh } from "lucide-react";
import type { Incident } from "@/types";

const EXAMPLE_ERRORS = [
  "Back-off restarting failed container\nError: CrashLoopBackOff\nkubectl get pods -n production",
  "OOMKilled: Container exceeded memory limit of 512Mi",
  "Error: creating resource group: storage account already exists\nTerraformError on main.tf line 42",
  "GitHub Actions: Process completed with exit code 1\nError: npm test failed with 3 failed assertions",
];

export default function IncidentsPage() {
  const [input, setInput] = useState("");
  const [result, setResult] = useState<Incident | null>(null);

  const analyze = useMutation({
    mutationFn: (raw: string) => analyzeIncident(raw, true),
    onSuccess: (data) => setResult(data),
  });

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <AlertTriangle className="text-yellow-400" /> Incident Analyzer
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Paste your error, get a root cause analysis + a meme to cope.
        </p>
      </div>

      <div className="p-5 rounded-xl border border-border bg-card space-y-4">
        <div>
          <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2 block">
            Error / Log / Alert
          </label>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Paste CrashLoopBackOff, OOMKilled, Terraform error, GitHub Actions failure..."
            rows={8}
            className="w-full px-3 py-2 rounded-lg bg-muted border border-border font-mono text-sm resize-none focus:outline-none focus:ring-1 focus:ring-purple-500"
          />
        </div>

        <div className="flex flex-wrap gap-2">
          <span className="text-xs text-muted-foreground self-center">Examples:</span>
          {EXAMPLE_ERRORS.map((ex, i) => (
            <button
              key={i}
              onClick={() => setInput(ex)}
              className="text-xs px-2 py-1 rounded bg-muted hover:bg-muted/80 text-muted-foreground transition-colors"
            >
              Example {i + 1}
            </button>
          ))}
        </div>

        <button
          onClick={() => input.trim() && analyze.mutate(input)}
          disabled={analyze.isPending || !input.trim()}
          className="w-full py-3 rounded-lg bg-yellow-600 hover:bg-yellow-700 disabled:opacity-50 text-white font-semibold flex items-center justify-center gap-2 transition-colors"
        >
          {analyze.isPending ? (
            <><Loader2 className="w-4 h-4 animate-spin" /> Analyzing...</>
          ) : (
            <><AlertTriangle className="w-4 h-4" /> Analyze + Generate Meme</>
          )}
        </button>
      </div>

      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-5 rounded-xl border border-yellow-500/30 bg-card space-y-4"
          >
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded-full bg-yellow-500/20 text-yellow-400 text-xs font-mono">
                {result.error_type}
              </span>
            </div>

            <div className="space-y-3">
              <div className="p-3 rounded-lg bg-muted">
                <div className="flex items-center gap-1.5 mb-1 text-xs font-semibold text-muted-foreground">
                  <Wrench className="w-3 h-3" /> Root Cause
                </div>
                <p className="text-sm">{result.root_cause}</p>
              </div>

              <div className="p-3 rounded-lg bg-muted">
                <div className="flex items-center gap-1.5 mb-1 text-xs font-semibold text-muted-foreground">
                  <Wrench className="w-3 h-3" /> Suggested Fix
                </div>
                <p className="text-sm">{result.suggested_fix}</p>
              </div>

              <div className="p-3 rounded-lg bg-purple-500/10 border border-purple-500/20">
                <div className="flex items-center gap-1.5 mb-1 text-xs font-semibold text-purple-400">
                  <Laugh className="w-3 h-3" /> Coping Mechanism
                </div>
                <p className="text-sm font-mono whitespace-pre-line">{result.funny_caption}</p>
              </div>
            </div>

            {result.image_url && (
              <div className="relative aspect-square max-w-sm mx-auto rounded-xl overflow-hidden">
                <Image src={result.image_url} alt="Incident meme" fill className="object-cover" />
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
