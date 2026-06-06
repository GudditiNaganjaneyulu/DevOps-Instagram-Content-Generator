"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useGenerate } from "@/hooks/useGenerate";
import { useGenerationStore } from "@/stores/generation";
import Image from "next/image";
import { Download, RefreshCw, Wand2, Copy, Check } from "lucide-react";
import { downloadImage } from "@/lib/api";
import { CATEGORY_LABELS, CATEGORY_EMOJIS } from "@/lib/utils";
import type { ContentCategory, ContentTone, ContentType } from "@/types";

const CATEGORIES = Object.keys(CATEGORY_LABELS) as ContentCategory[];
const TONES: ContentTone[] = ["sarcastic", "empathetic", "dark_humor", "motivational", "educational"];
const TYPES: ContentType[] = ["meme", "comic", "incident", "trend"];

export default function GeneratePage() {
  const { result, isGenerating, request, updateRequest } = useGenerationStore();
  const generate = useGenerate();
  const [copied, setCopied] = useState(false);
  const [context, setContext] = useState("");

  const handleGenerate = () => {
    generate.mutate({
      category: request.category ?? "kubernetes",
      tone: request.tone ?? "sarcastic",
      content_type: request.content_type ?? "meme",
      include_image: request.include_image ?? true,
      context: context || undefined,
    });
  };

  const copyCaption = () => {
    if (result?.caption) {
      navigator.clipboard.writeText(
        `${result.caption}\n\n${result.hashtags?.map((h) => `#${h}`).join(" ")}`
      );
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Generation Studio</h1>
        <p className="text-sm text-muted-foreground mt-1">Configure and generate DevOps humor content.</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Controls */}
        <div className="space-y-5 p-5 rounded-xl border border-border bg-card">
          <div>
            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2 block">
              Category
            </label>
            <div className="grid grid-cols-3 gap-2">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat}
                  onClick={() => updateRequest({ category: cat })}
                  className={`px-2 py-2 rounded-lg text-xs font-medium transition-colors flex flex-col items-center gap-1 ${
                    request.category === cat
                      ? "bg-purple-600/30 text-purple-300 border border-purple-500/50"
                      : "bg-muted text-muted-foreground hover:text-foreground border border-transparent"
                  }`}
                >
                  <span>{CATEGORY_EMOJIS[cat]}</span>
                  <span>{CATEGORY_LABELS[cat]}</span>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2 block">Tone</label>
            <div className="flex flex-wrap gap-2">
              {TONES.map((t) => (
                <button
                  key={t}
                  onClick={() => updateRequest({ tone: t })}
                  className={`px-3 py-1.5 rounded-lg text-xs capitalize transition-colors ${
                    request.tone === t ? "bg-purple-600 text-white" : "bg-muted text-muted-foreground hover:bg-muted/80"
                  }`}
                >
                  {t.replace("_", " ")}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2 block">
              Optional Context
            </label>
            <textarea
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="e.g. 'My pod crashed 3 times at 2am during deploy freeze'"
              rows={3}
              className="w-full px-3 py-2 rounded-lg bg-muted border border-border text-sm resize-none focus:outline-none focus:ring-1 focus:ring-purple-500"
            />
          </div>

          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="w-full py-3 rounded-lg bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white font-semibold flex items-center justify-center gap-2 transition-colors"
          >
            {isGenerating ? (
              <><RefreshCw className="w-4 h-4 animate-spin" /> Generating...</>
            ) : (
              <><Wand2 className="w-4 h-4" /> Generate</>
            )}
          </button>
        </div>

        {/* Result */}
        <AnimatePresence mode="wait">
          {result ? (
            <motion.div
              key={result.id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-4 p-5 rounded-xl border border-border bg-card"
            >
              {result.image_url && (
                <div className="relative aspect-square rounded-lg overflow-hidden">
                  <Image
                    src={result.thumbnail_url ?? result.image_url}
                    alt="Generated DevOps meme"
                    fill
                    className="object-cover"
                  />
                </div>
              )}
              {result.joke_text && (
                <div className="p-3 rounded-lg bg-muted font-mono text-sm whitespace-pre-line">
                  {result.joke_text}
                </div>
              )}
              {result.caption && (
                <div className="space-y-1">
                  <p className="text-sm">{result.caption}</p>
                  {result.hashtags?.length > 0 && (
                    <p className="text-xs text-purple-400">
                      {result.hashtags.map((h) => `#${h}`).join(" ")}
                    </p>
                  )}
                </div>
              )}
              <div className="flex gap-2">
                <button
                  onClick={copyCaption}
                  className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg bg-muted text-sm hover:bg-muted/80 transition-colors"
                >
                  {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                  {copied ? "Copied!" : "Copy Caption"}
                </button>
                {result.image_url && (
                  <a
                    href={downloadImage(result.id)}
                    download
                    className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg bg-purple-600 text-white text-sm hover:bg-purple-700 transition-colors"
                  >
                    <Download className="w-4 h-4" /> Download
                  </a>
                )}
              </div>
              <p className="text-xs text-muted-foreground text-center">
                {result.text_provider} · {result.generation_time_ms}ms
              </p>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center justify-center h-64 rounded-xl border border-dashed border-border text-muted-foreground text-sm"
            >
              Your generated content will appear here
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
