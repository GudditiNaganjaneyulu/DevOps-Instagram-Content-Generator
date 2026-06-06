"use client";
import { useInfiniteQuery } from "@tanstack/react-query";
import { fetchGallery } from "@/lib/api";

export function useGallery(category?: string) {
  return useInfiniteQuery({
    queryKey: ["gallery", category],
    queryFn: ({ pageParam = 1 }) =>
      fetchGallery({ category, page: pageParam as number, limit: 20 }),
    initialPageParam: 1,
    getNextPageParam: (last) =>
      last.page < last.pages ? last.page + 1 : undefined,
  });
}
