"""
Architecture diagram — DevOps Runtime Emotions AI Studio
Output: docs/architecture.png
"""
import os
os.makedirs("docs", exist_ok=True)

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import User
from diagrams.programming.framework import FastAPI, React
from diagrams.programming.language import Python, TypeScript
from diagrams.onprem.database import MongoDB
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.monitoring import Grafana
from diagrams.saas.identity import Auth0
from diagrams.generic.storage import Storage
from diagrams.generic.compute import Rack
from diagrams.onprem.ci import GithubActions
from diagrams.saas.chat import Slack

graph_attr = {
    "fontsize":  "26",
    "bgcolor":   "white",
    "pad":       "1.0",
    "splines":   "curved",
    "nodesep":   "0.6",
    "ranksep":   "1.4",
    "fontname":  "Helvetica Neue Bold",
    "labelloc":  "t",
}

node_attr = {
    "fontsize": "12",
    "fontname": "Helvetica Neue",
    "width":    "1.3",
}

with Diagram(
    "DevOps Runtime Emotions AI Studio — Architecture",
    filename="docs/architecture",
    outformat="png",
    show=False,
    direction="TB",
    graph_attr=graph_attr,
    node_attr=node_attr,
):
    user = User("User\n(Browser)")

    # ── CI/CD ──────────────────────────────────────────────────────
    cicd = GithubActions("GitHub Actions\nCI · Deploy Hooks")

    # ── Frontend ───────────────────────────────────────────────────
    with Cluster("Frontend  ·  Netlify CDN"):
        fe      = React("Next.js 15\nReact 19 · TypeScript")
        nextauth = TypeScript("NextAuth v5\nGoogle OAuth")

    # ── Auth ───────────────────────────────────────────────────────
    with Cluster("Auth"):
        google = Auth0("Google OAuth\n+ JWT  HS256")

    # ── Social Sharing ─────────────────────────────────────────────
    with Cluster("Social Sharing"):
        wa = Slack("WhatsApp\nWeb API")
        ig = Slack("Instagram\nWeb Share API\n(mobile file share)")

    # ── Backend ────────────────────────────────────────────────────
    with Cluster("Backend  ·  Render.com  ·  FastAPI  ·  Python 3.12"):

        api = FastAPI("FastAPI\nREST API")

        # Text Engine
        with Cluster("Text Engine  —  4-provider fallback"):
            t1 = Rack("OpenAI\ngpt-4o-mini")
            t2 = Rack("Groq\nllama-3.3-70b")
            t3 = Rack("Gemini\n2.0-flash")
            t4 = Rack("OpenRouter\nfree models")
            t1 >> Edge(label="429→", style="dashed", color="#e74c3c") >> t2
            t2 >> Edge(style="dashed", color="#e74c3c") >> t3
            t3 >> Edge(style="dashed", color="#e74c3c") >> t4

        # Image Engine
        with Cluster("Image Engine  —  5-provider fallback"):
            i1 = Python("TextCard\nPillow  ★ always first")
            i2 = Rack("Pollinations\n.ai")
            i3 = Rack("Stable Horde\nasync poll")
            i4 = Rack("HuggingFace\nSD 1.5")
            i5 = Rack("Gemini\nImage Gen")
            i1 >> Edge(style="dashed", color="#e74c3c") >> i2
            i2 >> Edge(style="dashed", color="#e74c3c") >> i3
            i3 >> Edge(style="dashed", color="#e74c3c") >> i4
            i4 >> Edge(style="dashed", color="#e74c3c") >> i5

        # Services
        with Cluster("Services"):
            sched    = Python("APScheduler\ndaily posts")
            trend    = Python("Trend Engine\nReddit · HN")
            incident = Python("Incident\nAnalyzer")

        # Observability
        with Cluster("Observability  —  structlog JSON"):
            log_handler = Python("_LokiHandler\nHTTP push")
            otlp        = Rack("OTLP Exporter\nTraces → Tempo")

    # ── Data Layer ─────────────────────────────────────────────────
    with Cluster("Data Layer"):
        mongo  = MongoDB("MongoDB Atlas\n512 MB")
        redis  = Redis("Upstash Redis\n10K cmd/day")
        cdn    = Storage("Cloudinary\n25 GB CDN")

    # ── Grafana Cloud ──────────────────────────────────────────────
    with Cluster("Grafana Cloud  ·  Observability"):
        loki  = Grafana("Loki\nLog Storage")
        tempo = Grafana("Tempo\nTrace Storage")
        dash  = Grafana("Dashboards\nLogQL Panels")
        loki  >> dash
        tempo >> dash

    # ── Edges ──────────────────────────────────────────────────────
    user >> Edge(label="HTTPS") >> fe
    fe   >> Edge(label="Google OAuth") >> nextauth
    nextauth >> Edge(label="verify token") >> google
    google   >> Edge(label="JWT issued") >> api

    fe >> Edge(label="REST  ·  Authorization: Bearer JWT") >> api

    cicd >> Edge(label="auto-deploy") >> fe
    cicd >> Edge(label="render deploy hook") >> api

    api >> Edge(label="text prompt") >> t1
    api >> Edge(label="image prompt") >> i1

    api >> Edge(label="read / write") >> mongo
    api >> Edge(label="rate limit · cache") >> redis
    api >> Edge(label="upload PNG") >> cdn
    cdn >> Edge(label="CDN URL") >> api

    api >> log_handler
    api >> otlp
    log_handler >> Edge(label="JSON log streams") >> loki
    otlp        >> Edge(label="OTLP spans") >> tempo

    api >> sched
    api >> trend
    api >> incident

    fe >> Edge(label="caption + image URL") >> wa
    fe >> Edge(label="Blob file · nav.share()") >> ig
