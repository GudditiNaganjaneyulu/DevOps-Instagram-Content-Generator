"use client";
import { useQuery } from "@tanstack/react-query";
import { fetchAnalyticsSummary, fetchUsageBreakdown } from "@/lib/api";

export function useAnalyticsSummary() {
  return useQuery({
    queryKey: ["analytics"],
    queryFn: fetchAnalyticsSummary,
    refetchInterval: 30000,
  });
}

export function useUsageBreakdown() {
  return useQuery({
    queryKey: ["analytics", "usage"],
    queryFn: fetchUsageBreakdown,
  });
}
