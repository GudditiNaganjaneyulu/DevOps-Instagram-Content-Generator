SYSTEM_PROMPT = """You are a DevOps humor writer creating Instagram content inspired by the @runtimeemotions style.
Your content captures the raw, emotional reality of DevOps, SRE, and Cloud Engineering life — with a strong Indian IT flavor.

IMPORTANT: Never use real company names. Use fictional archetypes everyone recognizes:
- "The Service Company" (large IT services firm archetype)
- "The MNC" (multinational IT company archetype)
- "The Startup" (funded startup archetype)
- "The Product Company" (tech product firm)
- "The Bank Project" (financial client archetype)
- "The Client" (the mysterious offshore client)

Indian IT context to weave in naturally:
- Pain points: appraisal season, variable pay cut, "onsite opportunity", band promotions, manager pinging at 11pm, "do the needful", weekend deployments, EOD reports, JIRA tickets, "revert back", "prepone the call", bench anxiety, PIP threats
- Characters: The Manager, The Client, The Fresher, The Senior Dev, The Scrum Master, The HR, The On-Call, The Architect Who Never Codes
- Expressions: "arre yaar", "kya scene hai", "it is what it is", "we'll manage", "jugaad fix", "out of station", "discuss offline", "loop in", "take this forward"
- Scenarios: Friday 5pm prod deploy, 3% hike "as per market standard", "career-defining project", 2am hotfix, "client is very happy" but no hike, bench for 6 months

Write original, relatable content that Indian DevOps engineers will instantly recognize.
Format responses as valid JSON only."""

SYSTEM_PROMPT_FEELINGS = """You are Runtime.xFeelings — a poet who expresses human emotions through programming metaphors.
Your style: short, raw, poetic quotes where ALL KEY WORDS are CAPITALIZED.
Inspired by @runtimeemotions. Topics: love, heartbreak, trust, loneliness, growth, healing.
Every quote uses a programming/tech concept as a metaphor for a human feeling.
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
    "feelings": "Runtime.xFeelings — programming metaphors for human emotions: love, heartbreak, trust, healing, loneliness",
}

FEELINGS_THEMES = {
    "love": "love, connection, being found, warmth, belonging — expressed through programming metaphors",
    "heartbreak": "heartbreak, loss, being deprecated, errors, crashes — the end of a relationship in code",
    "healing": "recovery, patching bugs, system restore, returning to LOCALHOST, rebuilding",
    "trust": "trust, authentication, SSL handshakes, commit history, being verified",
    "loneliness": "loneliness, null references, empty arrays, unread comments, undefined",
    "growth": "growth, refactoring, version upgrades, becoming a better build, deploying a new self",
}

TONE_INSTRUCTIONS = {
    "sarcastic": "Use dry, sarcastic humor. The kind engineers use at 3am during an incident.",
    "empathetic": "Show empathy and solidarity — we've all been there. Warm but relatable.",
    "dark_humor": "Dark tech humor — laugh at the chaos because crying won't fix the pod.",
    "motivational": "Ironic motivational — the 'you can do it' that only makes sense at 3am.",
    "educational": "Humor mixed with a real technical insight — funny but you learn something.",
    "poetic": "Quiet, emotional, poetic. Like reading code comments left by someone heartbroken.",
    "desi": "Indian IT humor — mix Hindi/English ('arre yaar', 'kya scene hai'), reference appraisals, onsite dreams, manager pings, jugaad fixes. Never name real companies — use 'The Service Company', 'The MNC', 'The Client'. Funny because every Indian developer lives this.",
}


def build_meme_prompt(category: str, tone: str, context: str | None = None) -> str:
    if category == "feelings":
        return build_feelings_prompt(tone, context)

    cat_context = CATEGORY_CONTEXTS.get(category, "DevOps engineering in general")
    tone_instr = TONE_INSTRUCTIONS.get(tone, TONE_INSTRUCTIONS["sarcastic"])
    extra = f"\nExtra context from user: {context}" if context else ""

    return f"""Create an original DevOps humor Instagram post about: {cat_context}
{tone_instr}{extra}

CRITICAL FORMAT RULES for joke_text:
- Use \\n to separate each line (4 to 7 lines total)
- Max 32 characters per line
- CAPITALIZE all key DevOps/tech words: DEPLOY, POD, NULL, ERROR, CRASH, LOOP, TIMEOUT, ALERT, BUILD, MERGE, GIT, K8S, AWS, IAM, CPU, MEMORY, LOG, etc.
- Write in short punchy statement/poetry style — NOT as a long dialogue paragraph
- Think @runtimeemotions Instagram style: emotional, relatable, hits different

Good example formats:
"THE DEPLOY passed.\\nThe TESTS passed.\\nThe USER found a BUG\\nin thirty seconds.\\nWe don't talk about it."

Indian style example:
"MANAGER at 11pm:\\nPlease DEPLOY tonight.\\n\\nDEV at 11pm:\\nSir it is FRIDAY.\\n\\nMANAGER:\\nYes very good ATTITUDE."

Return ONLY this JSON (no markdown, no extra text):
{{
  "joke_text": "4-7 short lines separated by \\n, key words ALL_CAPS, max 32 chars per line",
  "caption": "Instagram caption (2-3 sentences, conversational, ends with a hook or question)",
  "hashtags": ["list", "of", "15", "relevant", "hashtags", "no", "hash", "symbol"],
  "image_prompt": "Detailed prompt for generating a 1080x1080 Instagram illustration. Cartoon style, expressive character(s), vibrant but dark tech aesthetic, emotional storytelling, modern flat design, DevOps themed scene. No text in image."
}}"""


def build_feelings_prompt(tone: str, context: str | None = None) -> str:
    import random
    theme_key = context if context in FEELINGS_THEMES else random.choice(list(FEELINGS_THEMES.keys()))
    theme = FEELINGS_THEMES[theme_key]
    extra = f"\nFocus theme: {theme}"

    return f"""Create an original Runtime.xFeelings Instagram quote about: {theme}

Rules:
- 4 to 8 lines total, each line punchy and short
- Capitalize ALL key programming/emotion words (BOOLEAN, RETURN, LOCALHOST, LOOP, NULL, FOUND, etc.)
- Start with a bold statement: "X is NOT a Y." or "I was just a X." or "You are my X."
- Use programming concepts as metaphors: functions, loops, errors, deployments, commits, debugging
- End with an emotional punchline — something that hits
- Tone: {TONE_INSTRUCTIONS.get(tone, TONE_INSTRUCTIONS["poetic"])}{extra}

Examples of the style (do NOT copy, create original):
- "Love is NOT a BOOLEAN. You can't just assign a value and expect it to RUN forever."
- "You are my LOCALHOST. No matter how far the DEPLOYMENT takes me, I will always RETURN to you."
- "I was just a COMMENT. You parsed every line, but still CHOSE to IGNORE me."

Return ONLY this JSON:
{{
  "joke_text": "The 4-8 line quote. CAPITALIZE key emotional/programming words. Raw, poetic, instantly relatable.",
  "caption": "Instagram caption (1-2 sentences, personal and warm, ends with a question or reflection)",
  "hashtags": ["runtimeemotions", "programminglife", "developerquotes", "codingquotes", "techhumor", "runtimexfeelings", "programminghumor", "developerlife", "softwareengineering", "codepoetry", "techpoetry", "devlife", "programmingmemes", "coderlife", "devquotes"],
  "image_prompt": "Dark background, monospace font, syntax-highlighted text card, @runtimeemotions style, 1080x1080"
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
