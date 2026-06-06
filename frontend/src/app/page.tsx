import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4 py-20 bg-background">
      <div className="text-center max-w-3xl mx-auto space-y-8">
        <div className="space-y-4">
          <p className="text-sm font-mono text-purple-400 tracking-widest uppercase">
            AI-Powered DevOps Humor Studio
          </p>
          <h1 className="text-5xl sm:text-7xl font-bold tracking-tight gradient-text">
            Runtime Emotions
          </h1>
          <p className="text-xl text-muted-foreground leading-relaxed">
            Auto-generate DevOps memes, incident comics, and Kubernetes trauma —
            <br className="hidden sm:block" />
            powered entirely by free AI.
          </p>
        </div>

        <div className="flex flex-wrap gap-4 justify-center">
          <Link
            href="/login"
            className="px-8 py-3 rounded-lg bg-purple-600 hover:bg-purple-700 text-white font-semibold transition-colors"
          >
            Start Creating
          </Link>
          <a
            href="https://github.com/GudditiNaganjaneyulu/DevOps-Instagram-Content-Generator"
            target="_blank"
            rel="noopener noreferrer"
            className="px-8 py-3 rounded-lg border border-border hover:bg-muted text-foreground font-semibold transition-colors"
          >
            View on GitHub
          </a>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-8">
          {[
            { emoji: "⎈", label: "Kubernetes" },
            { emoji: "🏗️", label: "Terraform" },
            { emoji: "🚨", label: "Incidents" },
            { emoji: "📊", label: "Trends" },
          ].map(({ emoji, label }) => (
            <div key={label} className="p-4 rounded-xl border border-border bg-card text-center">
              <div className="text-3xl mb-2">{emoji}</div>
              <div className="text-sm text-muted-foreground">{label}</div>
            </div>
          ))}
        </div>

        <div className="pt-4 flex flex-wrap justify-center gap-3 text-xs text-muted-foreground">
          {["Groq", "Gemini", "Pollinations.ai", "MongoDB Atlas", "Vercel", "Render"].map((s) => (
            <span key={s} className="px-2 py-1 rounded border border-border">{s}</span>
          ))}
        </div>
      </div>
    </main>
  );
}
