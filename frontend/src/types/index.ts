export type ContentCategory =
  | "kubernetes" | "docker" | "terraform" | "aws" | "azure" | "gcp"
  | "cicd" | "incident" | "observability" | "security" | "platform" | "sre" | "ai_engineering";

export type ContentTone = "sarcastic" | "empathetic" | "dark_humor" | "motivational" | "educational";
export type ContentType = "meme" | "comic" | "incident" | "trend";
export type GenerationStatus = "pending" | "processing" | "completed" | "failed";

export interface Generation {
  id: string;
  user_id: string;
  status: GenerationStatus;
  category: ContentCategory;
  content_type: ContentType;
  tone: ContentTone;
  joke_text?: string;
  caption?: string;
  hashtags: string[];
  image_prompt?: string;
  image_url?: string;
  thumbnail_url?: string;
  text_provider?: string;
  image_provider?: string;
  generation_time_ms?: number;
  error_message?: string;
  created_at: string;
}

export interface GenerateRequest {
  category: ContentCategory;
  tone: ContentTone;
  content_type: ContentType;
  context?: string;
  include_image: boolean;
  image_style?: string;
}

export interface GalleryResponse {
  items: Generation[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface Incident {
  id: string;
  user_id: string;
  raw_input: string;
  error_type: string;
  root_cause: string;
  funny_caption: string;
  suggested_fix: string;
  joke_text?: string;
  image_url?: string;
  generation_id?: string;
  created_at: string;
}

export interface Trend {
  id: string;
  title: string;
  url?: string;
  source: "reddit" | "hackernews" | "k8s_blog" | "aws_blog";
  score: number;
  comments: number;
  category: string;
  summary?: string;
  image_url?: string;
  fetched_at: string;
}

export interface AnalyticsSummary {
  total_images: number;
  completed: number;
  failed: number;
  success_rate: number;
  user_total: number;
  today_count: number;
  providers: Record<string, number>;
}

export interface UserUsage {
  total_generations: number;
  today_count: number;
  total_downloads: number;
}

export interface User {
  id: string;
  email: string;
  name: string;
  image?: string;
  role: "user" | "admin";
  usage: UserUsage;
}
