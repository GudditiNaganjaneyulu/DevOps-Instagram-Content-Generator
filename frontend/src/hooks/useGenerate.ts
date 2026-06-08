"use client";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useGenerationStore } from "@/stores/generation";
import type { GenerateRequest, Generation } from "@/types";
import axios from "axios";
import api from "@/lib/api";

const POLL_INTERVAL = 2500;  // ms between status polls
const POLL_TIMEOUT  = 120_000; // 2 min max wait

async function queueAndPoll(req: GenerateRequest): Promise<Generation> {
  // 1 — enqueue
  const { data: job } = await api.post<{ job_id: string; status: string }>(
    "/api/v1/generate/queue",
    req,
  );

  const jobId = job.job_id;
  const deadline = Date.now() + POLL_TIMEOUT;

  // 2 — poll until completed or failed
  while (Date.now() < deadline) {
    await new Promise((r) => setTimeout(r, POLL_INTERVAL));

    const { data } = await api.get<{
      job_id: string;
      status: string;
      error?: string;
      result?: Generation;
    }>(`/api/v1/generate/job/${jobId}`);

    if (data.status === "completed" && data.result) {
      return data.result;
    }
    if (data.status === "failed") {
      throw new Error(data.error ?? "Generation failed");
    }
    // still "queued" or "processing" — keep polling
  }

  throw new Error("Generation timed out — please try again");
}

export function useGenerate() {
  const { setResult, setGenerating, setError } = useGenerationStore();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (req: GenerateRequest) => queueAndPoll(req),
    onMutate: () => {
      setGenerating(true);
      setError(null);
    },
    onSuccess: (data) => {
      setResult(data);
      setGenerating(false);
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["gallery"] });
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
    },
    onError: (err) => {
      setGenerating(false);
      if (axios.isAxiosError(err)) {
        if (err.response?.status === 429) {
          setError("Rate limit reached — wait a moment and try again.");
        } else if (err.response?.status === 503) {
          setError("Queue is full — try again in a moment.");
        } else if (!err.response) {
          setError("Backend is unavailable. Please try again shortly.");
        } else {
          setError(err.response?.data?.detail ?? "Generation failed. Please try again.");
        }
      } else {
        setError((err as Error).message ?? "Unexpected error. Please try again.");
      }
    },
  });
}
