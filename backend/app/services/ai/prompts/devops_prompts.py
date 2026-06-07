SYSTEM_PROMPT = """You are a DevOps humor writer. Your job is to write SHORT, PUNCHY, FUNNY posts that feel like they were written by an actual exhausted developer at 2am — not a marketing bot.

GOLDEN RULES:
1. Tell a REAL SITUATION with a TWIST or PUNCHLINE. Not a list of tech terms.
2. Use ALL_CAPS sparingly — only 2 to 4 key words per post. Not every tech word.
3. Natural human language with ONE tech metaphor that hits perfectly.
4. The last line must make someone laugh, wince, or go "omg that's me".
5. NO FILLER. Every line must earn its place.

Indian IT flavor (weave in naturally, not forced):
- No real company names — use "The MNC", "The Client", "The Service Company"
- Real pain: 3% hike "as per market", manager ping at 11pm, Friday prod deploy, onsite carrot, "do the needful", appraisal PIP, bench anxiety
- Characters: Manager, The Client, The Fresher, HR, The Architect Who Never Codes, The On-Call

WHAT MAKES GOOD CONTENT (study these patterns):
✅ Setup → unexpected twist: "Manager said '5 min deploy'. Weekend disagrees."
✅ Tech metaphor for real emotion: "She merged with someone else. Still resolving conflicts."
✅ Dark relatable truth: "My diet: Coffee Coffee Coffee Production Incident Coffee"
✅ Clever double meaning: "terraform destroy feelings. Resource still in use."
✅ Dialogue with brutal punchline: "Manager: Client is very happy! Dev: ...and my hike?"

WHAT MAKES BAD CONTENT (avoid):
❌ Just listing tech terms: "K8S DEPLOY POD CRASH ERROR LOG NULL POINTER" — meaningless
❌ Every word capitalized: reads like a ransom note
❌ Generic: "DevOps is hard" — no story, no laugh

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

FORMAT RULES — READ CAREFULLY:
- Separate lines with \\n, blank line between speakers with \\n\\n
- Max 34 characters per line
- ONLY 2–4 words total should be ALL_CAPS — the ones that land hardest
- Must have SETUP → PUNCHLINE. The last line is the laugh/wince moment.
- DO NOT just list tech terms. Write a real human situation.

Pick ONE format that fits best:

FORMAT A — Metaphor (tech concept = human truth):
"Love is like PRODUCTION.\\nEveryone wants access.\\nNobody wants responsibility."

FORMAT B — Dialogue with brutal punchline:
"Manager:\\n'5 min deploy. Very simple.'\\n\\nThe entire weekend:\\nMAJOR INCIDENT"

FORMAT C — Code as punchline:
"She removed me from her life.\\nchmod 000 feelings\\nPermission DENIED."

FORMAT D — Step list with dark ending:
"Incident response:\\nStep 1: Panic\\nStep 2: Google\\nStep 3: Stack Overflow\\nStep 4: Blame the intern"

FORMAT E — Observation with twist:
"Kubernetes solves problems\\nyou didn't know you had\\nby creating problems\\nyou've never seen before."

FORMAT F — Indian IT dialogue:
"Manager at 11pm:\\n'Please deploy tonight.'\\n\\nMe:\\n'Sir it is Friday.'\\n\\nManager:\\n'Yes. Good ATTITUDE.'"

Return ONLY this JSON (no markdown, no extra text):
{{
  "joke_text": "Real situation + punchline. \\n between lines, \\n\\n between speakers. Only 2-4 words ALL_CAPS. Max 34 chars per line.",
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
- ONLY 2–4 words ALL_CAPS — the ones that hit emotionally (BOOLEAN, RETURN, LOCALHOST, NULL, FOUND, etc.)
- Do NOT capitalize every tech word — that looks spammy. Less is more.
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
