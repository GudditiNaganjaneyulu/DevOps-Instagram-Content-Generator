"use client";
import { useSession, signOut } from "next-auth/react";

export default function SettingsPage() {
  const { data: session } = useSession();

  return (
    <div className="max-w-xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">Manage your account and preferences.</p>
      </div>

      <div className="p-5 rounded-xl border border-border bg-card space-y-4">
        <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Account</h2>
        <div className="flex items-center gap-3">
          {session?.user?.image && (
            <img src={session.user.image} alt="avatar" className="w-10 h-10 rounded-full" />
          )}
          <div>
            <p className="font-medium text-sm">{session?.user?.name}</p>
            <p className="text-xs text-muted-foreground">{session?.user?.email}</p>
          </div>
        </div>
        <button
          onClick={() => signOut({ callbackUrl: "/" })}
          className="w-full py-2 rounded-lg border border-destructive text-destructive text-sm hover:bg-destructive hover:text-white transition-colors"
        >
          Sign Out
        </button>
      </div>

      <div className="p-5 rounded-xl border border-border bg-card space-y-3">
        <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Free Tier Status</h2>
        {[
          { label: "Groq", limit: "14,400 req/day", color: "bg-green-400" },
          { label: "Gemini", limit: "1,500 req/day", color: "bg-blue-400" },
          { label: "Pollinations.ai", limit: "Unlimited", color: "bg-purple-400" },
          { label: "Cloudinary", limit: "25 GB storage", color: "bg-orange-400" },
          { label: "MongoDB Atlas", limit: "512 MB", color: "bg-green-400" },
          { label: "Upstash Redis", limit: "10K cmds/day", color: "bg-red-400" },
        ].map(({ label, limit, color }) => (
          <div key={label} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${color}`} />
              <span className="text-sm">{label}</span>
            </div>
            <span className="text-xs text-muted-foreground">{limit}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
