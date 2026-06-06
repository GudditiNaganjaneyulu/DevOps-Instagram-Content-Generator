"use client";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { generateContent } from "@/lib/api";
import { useGenerationStore } from "@/stores/generation";
import type { GenerateRequest } from "@/types";

export function useGenerate() {
  const { setResult, setGenerating } = useGenerationStore();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (req: GenerateRequest) => generateContent(req),
    onMutate: () => setGenerating(true),
    onSuccess: (data) => {
      setResult(data);
      setGenerating(false);
      queryClient.invalidateQueries({ queryKey: ["gallery"] });
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
    },
    onError: () => setGenerating(false),
  });
}
