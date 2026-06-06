"use client";
import { useAnalyticsSummary, useUsageBreakdown } from "@/hooks/useAnalytics";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { Images, CheckCircle, AlertCircle, Zap, TrendingUp, Cpu } from "lucide-react";

export default function DashboardPage() {
  const { data: summary, isLoading } = useAnalyticsSummary();
  const { data: usage } = useUsageBreakdown();

  const stats = [
    { label: "Total Images", value: summary?.total_images ?? 0, icon: Images, color: "text-purple-400" },
    { label: "Today", value: summary?.today_count ?? 0, icon: Zap, color: "text-yellow-400" },
    { label: "Success Rate", value: `${summary?.success_rate ?? 0}%`, icon: CheckCircle, color: "text-green-400" },
    { label: "My Total", value: summary?.user_total ?? 0, icon: TrendingUp, color: "text-blue-400" },
  ];

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground text-sm mt-1">Your generation stats at a glance.</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="p-4 rounded-xl border border-border bg-card">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-muted-foreground">{label}</span>
              <Icon className={`w-4 h-4 ${color}`} />
            </div>
            <div className="text-2xl font-bold">{isLoading ? "—" : value}</div>
          </div>
        ))}
      </div>

      {usage?.daily_breakdown?.length > 0 && (
        <div className="p-5 rounded-xl border border-border bg-card">
          <h2 className="text-sm font-semibold mb-4 text-muted-foreground uppercase tracking-wide">
            30-Day Generation Activity
          </h2>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={usage.daily_breakdown.slice().reverse()}>
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#a855f7" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {summary?.providers && (
        <div className="p-5 rounded-xl border border-border bg-card">
          <h2 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">
            Provider Usage
          </h2>
          <div className="flex flex-wrap gap-3">
            {Object.entries(summary.providers).map(([provider, count]) => (
              <div key={provider} className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-muted text-sm">
                <Cpu className="w-3 h-3 text-purple-400" />
                <span className="font-mono text-xs">{provider}</span>
                <span className="text-muted-foreground">×{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
