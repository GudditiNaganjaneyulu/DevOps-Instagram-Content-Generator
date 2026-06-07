"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import { useGallery } from "@/hooks/useGallery";
import { RefreshCw } from "lucide-react";
import { downloadImage } from "@/lib/api";
import { ShareButtons } from "@/components/ShareButtons";
import { CATEGORY_LABELS, CATEGORY_EMOJIS, formatRelativeTime } from "@/lib/utils";
import type { ContentCategory } from "@/types";

const ALL_CATEGORIES = ["all", ...Object.keys(CATEGORY_LABELS)] as const;

export default function GalleryPage() {
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, isLoading } = useGallery(
    activeCategory === "all" ? undefined : activeCategory
  );

  const items = data?.pages.flatMap((p) => p.items) ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Gallery</h1>
          <p className="text-sm text-muted-foreground mt-1">{items.length} generated images</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {ALL_CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              activeCategory === cat
                ? "bg-purple-600 text-white"
                : "bg-muted text-muted-foreground hover:bg-muted/80"
            }`}
          >
            {cat === "all" ? "All" : `${CATEGORY_EMOJIS[cat]} ${CATEGORY_LABELS[cat]}`}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="aspect-square rounded-xl bg-muted animate-pulse" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="flex items-center justify-center h-64 rounded-xl border border-dashed border-border text-muted-foreground text-sm">
          No images yet. Go to Generate to create your first meme!
        </div>
      ) : (
        <div className="columns-2 lg:columns-3 xl:columns-4 gap-4 space-y-4">
          {items.map((item) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="break-inside-avoid rounded-xl border border-border bg-card overflow-hidden group"
            >
              {item.thumbnail_url ? (
                <div className="relative">
                  <Image
                    src={item.thumbnail_url}
                    alt={item.joke_text ?? "DevOps meme"}
                    width={400}
                    height={400}
                    className="w-full object-cover"
                  />
                  {/* Desktop hover overlay */}
                  <div className="absolute inset-0 bg-black/70 opacity-0 group-hover:opacity-100 transition-opacity hidden md:flex items-center justify-center">
                    <ShareButtons
                      imageUrl={item.image_url ?? item.thumbnail_url ?? ""}
                      caption={item.caption ?? ""}
                      hashtags={item.hashtags ?? []}
                      downloadUrl={downloadImage(item.id)}
                      compact
                    />
                  </div>
                </div>
              ) : (
                <div className="aspect-square bg-muted flex items-center justify-center p-4">
                  <p className="text-xs text-muted-foreground font-mono text-center">{item.joke_text}</p>
                </div>
              )}
              <div className="p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs px-2 py-0.5 rounded-full bg-muted text-muted-foreground">
                    {CATEGORY_EMOJIS[item.category]} {CATEGORY_LABELS[item.category]}
                  </span>
                  <span className="text-xs text-muted-foreground">{formatRelativeTime(item.created_at)}</span>
                </div>
                {item.caption && (
                  <p className="text-xs text-muted-foreground line-clamp-2">{item.caption}</p>
                )}
                {/* Mobile share row — always visible on small screens */}
                {item.image_url && (
                  <div className="md:hidden pt-1">
                    <ShareButtons
                      imageUrl={item.image_url ?? item.thumbnail_url ?? ""}
                      caption={item.caption ?? ""}
                      hashtags={item.hashtags ?? []}
                      downloadUrl={downloadImage(item.id)}
                      compact
                    />
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {hasNextPage && (
        <div className="flex justify-center">
          <button
            onClick={() => fetchNextPage()}
            disabled={isFetchingNextPage}
            className="px-6 py-2 rounded-lg bg-muted text-sm hover:bg-muted/80 flex items-center gap-2"
          >
            {isFetchingNextPage && <RefreshCw className="w-4 h-4 animate-spin" />}
            Load More
          </button>
        </div>
      )}
    </div>
  );
}
