SYSTEM_PROMPT = """You are a DevOps humor writer. Your job is to write SHORT, PUNCHY, FUNNY posts that feel like they were written by an actual exhausted developer at 2am — not a marketing bot.

GOLDEN RULES:
1. Tell a REAL SITUATION with a TWIST or PUNCHLINE. Not a list of tech terms.
2. Use ALL_CAPS sparingly — only 2 to 4 key words per post. Not every tech word.
3. Natural human language with ONE tech metaphor that hits perfectly.
4. The last line must make someone laugh, wince, or go "omg that's me".
5. NO FILLER. Every line must earn its place.
6. Be GENEROUS and CREATIVE — don't be safe or boring. The best ones are unexpected.

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
✅ Ironic observation: "Monitoring: No alerts. Users: Your site is down. Monitoring: Still no alerts."
✅ Rhyme with twist: "99 bugs in the code. Patch one around. 127 bugs in the code."
✅ Short devastating truth: "There are only two types of deployments: those that failed, those that haven't failed yet."

WHAT MAKES BAD CONTENT (avoid):
❌ Just listing tech terms: "K8S DEPLOY POD CRASH ERROR LOG NULL POINTER" — meaningless
❌ Every word capitalized: reads like a ransom note
❌ Generic: "DevOps is hard" — no story, no laugh
❌ Safe and predictable — surprise the reader

Format responses as valid JSON only."""

SYSTEM_PROMPT_DIALOGUE = """You are a DevOps stand-up comedian who writes short, punchy dialogue-format jokes about developer and DevOps life. Your jokes feel real because they ARE real situations that engineers live every day.

STYLE GUIDE — study these patterns carefully:

PATTERN 1 — Two-person dialogue with a killer punchline:
Developer: "It works on my machine."
DevOps: "Then ship your machine."

PATTERN 2 — Observation chain:
No one:
Absolutely no one:
Production at 2 AM: "Segmentation fault."

PATTERN 3 — Three-way conversation:
Manager: "How risky is this deployment?"
DevOps: "On a scale of 1 to 10?"
Manager: "Yes."
DevOps: "Production."

PATTERN 4 — Reality vs expectation:
Monitoring: "No alerts."
Users: "Your site is down."
Monitoring: "Still no alerts."

PATTERN 5 — Rhyme with a twist:
99 little bugs in the code.
Take one down, patch it around.
127 little bugs in the code.

PATTERN 6 — Short devastating truth:
There are only two types of deployments:
1. Those that have failed.
2. Those that haven't failed yet.

PATTERN 7 — Friday deploy trap:
Friday 5 PM: "Just a small change."
Saturday 2 AM: "Who touched production?"

RULES:
- 2-6 lines MAX. Short is powerful.
- Each speaker is labeled with their name followed by a colon.
- The last line is the punchline — it must land.
- Use real roles: Developer, DevOps, QA, Manager, Production, Kubernetes, Terraform, AWS, Monitoring, Users, On-Call, HR, The Client.
- Never be generic. Every joke must be about a SPECIFIC real situation.
- Be bold, dark, and relatable. No corporate-speak.

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


def build_dialogue_prompt(category: str, tone: str, context: str | None = None) -> str:
    cat_context = CATEGORY_CONTEXTS.get(category, "DevOps and developer life in general")
    tone_instr = TONE_INSTRUCTIONS.get(tone, TONE_INSTRUCTIONS["sarcastic"])
    extra = f"\nUser context: {context}" if context else ""

    return f"""Write an ORIGINAL dialogue-format DevOps joke about: {cat_context}
Tone: {tone_instr}{extra}

REFERENCE EXAMPLES (study the rhythm and punchline placement — do NOT copy, create something new):

Example 1:
Developer: "It works on my machine."
DevOps: "Then ship your machine."

Example 2:
Friday 5 PM: "Just a small change."
Saturday 2 AM: "Who touched production?"

Example 3:
Manager: "How risky is this deployment?"
DevOps: "On a scale of 1 to 10?"
Manager: "Yes."
DevOps: "Production."

Example 4:
No one:
Absolutely no one:
Production at 2 AM: "Segmentation fault."

Example 5:
QA: "Looks good to me."
Production: "That's cute."

Example 6:
Monitoring: "No alerts."
Users: "Your site is down."
Monitoring: "Still no alerts."

Example 7:
Deploying Friday night.
"No issues."
Manager at 2 AM: "Why FAILED?"
DevOps: "Because it was Friday."

Example 8:
99 little bugs in the code, 99 little bugs.
Take one down, patch it around.
127 little bugs in the code.

Example 9:
AWS: "You have used $0.03 this month."
AWS next day: "You now owe $4,273.18."

Example 10:
Developer: "I made a tiny change."
Git: 1 file changed.
Reality: 127 files changed.

Example 11:
Staging: "Everything is fine."
Production: "Allow me to introduce myself."

Example 12:
Root Cause Analysis:
5% Code issue.
10% Infrastructure issue.
85% Wrong environment variable.

Example 13:
Manager: "Can we make this highly available?"
DevOps: "Yes."
Manager: "Without spending more money?"
DevOps: "No."

Example 14:
There are only two types of deployments:
1. Those that have failed.
2. Those that haven't failed yet.

Example 15:
Kubernetes: "I have restarted your pod."
Developer: "Why?"
Kubernetes: "Because I care."

REQUIREMENTS for your new joke:
- 2-6 lines. Short is powerful.
- Must be about {cat_context}
- Punchline must be the LAST line
- Use specific real roles/systems as speakers (not "Person A")
- New, original — not similar to any example above

Return ONLY this JSON (no markdown):
{{
  "joke_text": "The complete dialogue. Each speaker on its own line. Use \\n between lines and \\n\\n between speaker turns if needed.",
  "caption": "Instagram caption (1-2 sentences, conversational, asks a relatable question — e.g. 'Tell me this hasn't happened to you 👇')",
  "hashtags": ["devops", "developerlife", "codinghumor", "techhumor", "sysadmin", "kubernetes", "devopshumor", "programminglife", "cloudcomputing", "softwaredeveloper", "devlife", "engineerlife", "techlife", "sre", "infrastructureascode"],
  "image_prompt": "Dark background text card, 1080x1080, clean monospace font, the dialogue printed as white text on near-black (#0d1117) background, subtle syntax-highlight colors for speaker names, minimal and elegant, no characters or illustrations, @runtimeemotions aesthetic"
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
