import axios from "axios";
import type {
  Generation, GenerateRequest, GalleryResponse,
  Incident, Trend, AnalyticsSummary,
} from "@/types";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

// Inject JWT from localStorage on every request
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Token storage helpers
export const setToken = (token: string) => localStorage.setItem("access_token", token);
export const clearToken = () => localStorage.removeItem("access_token");
export const getToken = () => (typeof window !== "undefined" ? localStorage.getItem("access_token") : null);

// Auth
export const authGoogle = (access_token: string) =>
  api.post<{ access_token: string; user: object }>("/api/v1/auth/google", { access_token, provider: "google" });

export const authGitHub = (access_token: string) =>
  api.post<{ access_token: string; user: object }>("/api/v1/auth/github", { access_token, provider: "github" });

// Generation
export const generateContent = (req: GenerateRequest) =>
  api.post<Generation>("/api/v1/generate/", req).then((r) => r.data);

export const getGenerationStatus = (id: string) =>
  api.get<Generation>(`/api/v1/generate/status/${id}`).then((r) => r.data);

// Gallery
export const fetchGallery = (params?: { category?: string; page?: number; limit?: number }) =>
  api.get<GalleryResponse>("/api/v1/gallery/", { params }).then((r) => r.data);

export const downloadImage = (id: string) =>
  `${process.env.NEXT_PUBLIC_API_URL}/api/v1/gallery/${id}/download`;

// Incidents
export const analyzeIncident = (raw_input: string, generate_image = true) =>
  api.post<Incident>("/api/v1/incidents/analyze", { raw_input, generate_image }).then((r) => r.data);

export const fetchIncidents = () =>
  api.get<Incident[]>("/api/v1/incidents/").then((r) => r.data);

// Trends
export const fetchTrends = (limit = 20) =>
  api.get<Trend[]>("/api/v1/trends/", { params: { limit } }).then((r) => r.data);

export const generateTrendMeme = (trend_id: string) =>
  api.post(`/api/v1/trends/${trend_id}/generate`).then((r) => r.data);

// Analytics
export const fetchAnalyticsSummary = () =>
  api.get<AnalyticsSummary>("/api/v1/analytics/summary").then((r) => r.data);

export const fetchUsageBreakdown = () =>
  api.get("/api/v1/analytics/usage").then((r) => r.data);

// Health
export const checkHealth = () =>
  api.get("/health").then((r) => r.data);

export default api;
