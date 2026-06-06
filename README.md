# DevOps Runtime Emotions AI Studio

> Auto-generate DevOps-themed Instagram humor — memes, comics, and incident posts — powered entirely by free AI providers.

Inspired by the emotional storytelling style of [@runtimeemotions](https://www.instagram.com/runtimeemotions), applied to the world of Kubernetes, Terraform, AWS, CI/CD, and SRE culture.

---

## Features

| Module | Description |
|---|---|
| **Prompt Engine** | Generates jokes, scenarios, captions, hashtags per DevOps category |
| **Image Engine** | 1080×1080 Instagram images via Pollinations.ai → HuggingFace |
| **Incident Analyzer** | Paste CrashLoopBackOff / OOMKilled errors → get a meme |
| **Trend Engine** | Scrapes Reddit + HackerNews → auto-generates trending memes |
| **Scheduler** | 1–5 posts daily, hands-free |
| **Gallery** | Browse, filter, and download all generated content |
| **Analytics** | Dashboard with AI usage, success rate, provider health |

---

## Tech Stack

```
Frontend  Next.js 15 · React 19 · TypeScript · Tailwind · ShadCN · Zustand · TanStack Query
Backend   FastAPI · Python 3.12 · Motor (MongoDB) · Redis · Pydantic v2
Database  MongoDB Atlas Free (512 MB)
Cache     Upstash Redis Free (10K cmds/day)
Storage   Cloudinary Free (25 GB)
Auth      NextAuth · Google OAuth · GitHub OAuth
AI Text   Groq (Llama 4) → Gemini (Google AI Studio) → OpenRouter
AI Image  Pollinations.ai → Hugging Face FLUX.1-schnell
Deploy    Vercel (frontend) · Render.com (backend)
```

---

## Quick Start

### Prerequisites
- Node.js 20+
- Python 3.12+
- Poetry
- Docker + Docker Compose

### 1. Clone & configure
```bash
git clone https://github.com/GudditiNaganjaneyulu/DevOps-Instagram-Content-Generator.git
cd DevOps-Instagram-Content-Generator
cp .env.example .env
# Edit .env — fill in your API keys
```

### 2. Run with Docker
```bash
make dev
```

### 3. Run locally
```bash
# Backend
cd backend
poetry install
poetry run uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## API Keys Needed (all free)

| Provider | Get Key At | Used For |
|---|---|---|
| Groq | https://console.groq.com | Text generation (primary) |
| Google AI Studio | https://aistudio.google.com/apikey | Gemini fallback |
| OpenRouter | https://openrouter.ai/keys | LLM last resort |
| Hugging Face | https://huggingface.co/settings/tokens | Image generation fallback |
| Cloudinary | https://cloudinary.com | Image storage/CDN |
| MongoDB Atlas | https://www.mongodb.com/atlas | Database |
| Upstash | https://upstash.com | Redis cache |
| Google Cloud | https://console.cloud.google.com | OAuth |
| GitHub | https://github.com/settings/developers | OAuth |

---

## Project Structure

```
devops-runtime-emotions/
├── frontend/          Next.js 15 app
├── backend/           FastAPI Python app
├── shared/            Shared enums/constants
├── docker/            Nginx + Prometheus configs
├── scripts/           DB seed, provider tests
├── .github/workflows/ CI/CD pipelines
├── docker-compose.yml Local dev stack
└── .env.example       Environment template
```

---

## Development

```bash
make test          # Run all tests
make lint          # Lint backend + frontend
make format        # Auto-format code
make seed          # Seed sample data
make clean         # Remove build artifacts
```

---

## Deployment

| Service | Platform | Config |
|---|---|---|
| Frontend | Vercel | Auto-deploys from main branch |
| Backend | Render.com | `render.yaml` |

See [docs/deployment.md](docs/deployment.md) for step-by-step instructions.

---

## License

MIT
