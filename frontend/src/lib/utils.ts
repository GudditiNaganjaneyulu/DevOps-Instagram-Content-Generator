import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateStr: string): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short", day: "numeric", year: "numeric",
  }).format(new Date(dateStr));
}

export function formatRelativeTime(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export const CATEGORY_LABELS: Record<string, string> = {
  kubernetes: "Kubernetes",
  docker: "Docker",
  terraform: "Terraform",
  aws: "AWS",
  azure: "Azure",
  gcp: "GCP",
  cicd: "CI/CD",
  incident: "Incident",
  observability: "Observability",
  security: "Security",
  platform: "Platform Eng",
  sre: "SRE",
  ai_engineering: "AI Engineering",
  feelings: "Feelings",
  general: "General",
};

export const CATEGORY_EMOJIS: Record<string, string> = {
  kubernetes: "⎈",
  docker: "🐳",
  terraform: "🏗️",
  aws: "☁️",
  azure: "🔷",
  gcp: "🌐",
  cicd: "🔄",
  incident: "🚨",
  observability: "📊",
  security: "🔒",
  platform: "🚀",
  sre: "🛡️",
  ai_engineering: "🤖",
  feelings: "💙",
  general: "😄",
};

export const CONTENT_TYPE_LABELS: Record<string, string> = {
  meme: "Meme",
  comic: "Comic",
  incident: "Incident",
  trend: "Trend",
  dialogue: "Dialogue",
};

export const CONTENT_TYPE_EMOJIS: Record<string, string> = {
  meme: "🎭",
  comic: "🖼️",
  incident: "🚨",
  trend: "📈",
  dialogue: "💬",
};
