SYSTEM_PROMPT = """You are a DevOps humor writer creating Instagram content inspired by the @runtimeemotions style.
Your content captures the raw, emotional reality of DevOps, SRE, and Cloud Engineering life.
Write original, relatable content that DevOps engineers will instantly recognize.
Format responses as valid JSON only."""

CATEGORY_CONTEXTS = {
    "kubernetes": "Kubernetes orchestration — pods crashing, deployments failing, CrashLoopBackOff, OOMKilled, scheduling issues",
    "docker": "Docker containers — build failures, layer caching, Dockerfile debugging, multi-stage builds",
    "terraform": "Terraform IaC — state conflicts, plan/apply anxiety, resource drift, provider errors",
    "aws": "AWS cloud — cost spikes, IAM permission errors, mysterious outages, service limits",
    "azure": "Azure cloud — ARM templates, AKS, DevOps pipelines, mysterious quota errors",
    "gcp": "GCP — GKE, Cloud Run, quotas, billing surprises",
    "cicd": "CI/CD pipelines — flaky tests, build timeouts, deploy failures, GitOps pain",
    "incident": "Incident response — 3am pages, postmortems, root cause analysis, runbooks",
    "observability": "Observability — Prometheus alerts firing at 3am, Datadog dashboards, Grafana, log archaeology",
    "security": "DevSecOps — CVE alerts, secret leaks, compliance scans, RBAC confusion",
    "platform": "Platform Engineering — Internal Developer Platforms, developer experience, golden paths",
    "sre": "SRE practices — error budgets, toil reduction, SLOs, capacity planning",
    "ai_engineering": "AI/ML Engineering — GPU costs, model deployment, MLOps, LLM rate limits",
}

TONE_INSTRUCTIONS = {
    "sarcastic": "Use dry, sarcastic humor. The kind engineers use at 3am during an incident.",
    "empathetic": "Show empathy and solidarity — we've all been there. Warm but relatable.",
    "dark_humor": "Dark tech humor — laugh at the chaos because crying won't fix the pod.",
    "motivational": "Ironic motivational — the 'you can do it' that only makes sense at 3am.",
    "educational": "Humor mixed with a real technical insight — funny but you learn something.",
}


def build_meme_prompt(category: str, tone: str, context: str | None = None) -> str:
    cat_context = CATEGORY_CONTEXTS.get(category, "DevOps engineering in general")
    tone_instr = TONE_INSTRUCTIONS.get(tone, TONE_INSTRUCTIONS["sarcastic"])
    extra = f"\nExtra context from user: {context}" if context else ""

    return f"""Create an original DevOps humor Instagram post about: {cat_context}
{tone_instr}{extra}

Return ONLY this JSON (no markdown, no extra text):
{{
  "joke_text": "2-4 line dialogue or scenario. Use character names like 'DevOps Engineer', 'Kubernetes', 'Terraform', 'The Alerting System', 'The On-Call', 'AWS Billing'. Make it emotionally resonant and instantly relatable.",
  "caption": "Instagram caption (2-3 sentences, conversational, ends with a hook or question)",
  "hashtags": ["list", "of", "15", "relevant", "hashtags", "no", "hash", "symbol"],
  "image_prompt": "Detailed prompt for generating a 1080x1080 Instagram illustration. Cartoon style, expressive character(s), vibrant but dark tech aesthetic, emotional storytelling, modern flat design, DevOps themed scene. No text in image."
}}"""


def build_incident_prompt(error_type: str, raw_input: str) -> str:
    return f"""Analyze this DevOps incident and create humor content.

Error type: {error_type}
Raw error/log: {raw_input[:500]}

Return ONLY this JSON:
{{
  "error_type": "classified error type",
  "root_cause": "1-2 sentence technical root cause analysis (accurate and helpful)",
  "funny_caption": "Hilarious but empathetic caption for an Instagram post about this incident",
  "suggested_fix": "1-2 sentence practical fix",
  "joke_text": "2-3 line dialogue capturing the emotional journey of this incident",
  "image_prompt": "Detailed prompt for a 1080x1080 cartoon illustration of this DevOps disaster moment"
}}"""


def build_trend_meme_prompt(title: str, source: str, category: str) -> str:
    return f"""Create a DevOps humor Instagram post inspired by this trending topic.

Topic: {title}
Source: {source}
Category: {category}

Return ONLY this JSON:
{{
  "joke_text": "Original humorous take on this trend, 2-4 lines, dialogue or scenario style",
  "caption": "Instagram caption connecting this trend to real DevOps experience",
  "hashtags": ["15", "relevant", "hashtags"],
  "image_prompt": "1080x1080 illustration prompt for this DevOps trend, cartoon style, expressive"
}}"""
