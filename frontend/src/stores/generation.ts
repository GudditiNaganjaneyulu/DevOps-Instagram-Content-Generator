import { create } from "zustand";
import type { Generation, GenerateRequest, ContentCategory, ContentTone, ContentType } from "@/types";

interface GenerationState {
  result: Generation | null;
  isGenerating: boolean;
  request: Partial<GenerateRequest>;
  setResult: (g: Generation | null) => void;
  setGenerating: (v: boolean) => void;
  updateRequest: (updates: Partial<GenerateRequest>) => void;
  reset: () => void;
}

const DEFAULT_REQUEST: Partial<GenerateRequest> = {
  category: "kubernetes",
  tone: "sarcastic",
  content_type: "meme",
  include_image: true,
  image_style: "dark_tech",
};

export const useGenerationStore = create<GenerationState>((set) => ({
  result: null,
  isGenerating: false,
  request: DEFAULT_REQUEST,
  setResult: (result) => set({ result }),
  setGenerating: (isGenerating) => set({ isGenerating }),
  updateRequest: (updates) => set((s) => ({ request: { ...s.request, ...updates } })),
  reset: () => set({ result: null, isGenerating: false, request: DEFAULT_REQUEST }),
}));
