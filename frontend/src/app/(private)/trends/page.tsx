"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import Image from "next/image";
import { fetchTrends, generateTrendMeme } from "@/lib/api";
import { TrendingUp, ExternalLink, Wand2, Loader2, Reddit } from "lucide-react";
import type { Trend } from "@/types";
import { formatRelativeTime } from "@/lib/utils";

const SOURCE_LABELS: Record<string, string> = {
  reddit: "Reddit",
  hackernews: "Hacker News",
  k8s_blog: "K8s Blog",
  aws_blog: "AWS Blog",
};

export default function TrendsPage() {
  const queryClient = useQueryClient();
  const { data: trends = [], isLoading } = useQuery({
    queryKey: ["trends"],
    queryFn: () => fetchTrends(20),
    staleTime: 1000 * 60 * 30,
  });

  const generate = useMutation({
    mutationFn: (id: string) => generateTrendMeme(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["trends"] }),
  });

  return (
    <div className="max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <TrendingUp className="text-green-400" /> Trending Topics
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Hot DevOps topics from Reddit & Hacker News. Generate a meme for any.
        </p>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-20 rounded-xl bg-muted animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {trends.map((trend: Trend, i: number) => (
            <motion.div
              key={trend.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.03 }}
              className="p-4 rounded-xl border border-border bg-card"
            >
              <div className="flex items-start gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs px-2 py-0.5 rounded-full bg-muted text-muted-foreground">
                      {SOURCE_LABELS[trend.source] ?? trend.source}
                    </span>
                    <span className="text-xs text-muted-foreground capitalize">{trend.category}</span>
                    <span className="text-xs text-muted-foreground">·</span>
                    <span className="text-xs text-muted-foreground">↑ {trend.score}</span>
                  </div>
                  <h3 className="text-sm font-medium line-clamp-2">{trend.title}</h3>
                  <div className="flex items-center gap-3 mt-2">
                    {trend.url && (
                      <a
                        href={trend.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-purple-400 flex items-center gap-1 hover:underline"
                      >
                        <ExternalLink className="w-3 h-3" /> View
                      </a>
                    )}
                    <span className="text-xs text-muted-foreground">{trend.comments} comments</span>
                  </div>
                </div>

                {trend.image_url ? (
                  <div className="w-16 h-16 rounded-lg overflow-hidden shrink-0">
                    <Image src={trend.image_url} alt="trend meme" width={64} height={64} className="object-cover" />
                  </div>
                ) : (
                  <button
                    onClick={() => generate.mutate(trend.id)}
                    disabled={generate.isPending}
                    className="shrink-0 flex items-center gap-1.5 px-3 py-2 rounded-lg bg-purple-600/20 text-purple-400 text-xs hover:bg-purple-600/30 transition-colors"
                  >
                    {generate.isPending ? (
                      <Loader2 className="w-3 h-3 animate-spin" />
                    ) : (
                      <Wand2 className="w-3 h-3" />
                    )}
                    Meme It
                  </button>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
