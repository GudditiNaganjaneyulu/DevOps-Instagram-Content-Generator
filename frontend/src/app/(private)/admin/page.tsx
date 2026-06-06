"use client";
import { useMutation, useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { Play, RefreshCw, Shield } from "lucide-react";

export default function AdminPage() {
  const { data: status } = useQuery({
    queryKey: ["scheduler-status"],
    queryFn: () => api.get("/api/v1/scheduler/status").then((r) => r.data),
    refetchInterval: 30000,
  });

  const trigger = useMutation({
    mutationFn: () => api.post("/api/v1/scheduler/run").then((r) => r.data),
  });

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Shield className="text-purple-400" /> Admin Panel
        </h1>
        <p className="text-sm text-muted-foreground mt-1">Admin-only controls.</p>
      </div>

      <div className="p-5 rounded-xl border border-border bg-card space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold">Scheduler</h2>
          <div className={`flex items-center gap-1.5 text-xs ${status?.running ? "text-green-400" : "text-muted-foreground"}`}>
            <div className={`w-2 h-2 rounded-full ${status?.running ? "bg-green-400" : "bg-muted-foreground"}`} />
            {status?.running ? "Running" : "Stopped"}
          </div>
        </div>

        {status?.jobs?.map((job: { id: string; next_run: string }) => (
          <div key={job.id} className="p-3 rounded-lg bg-muted text-sm">
            <span className="font-mono text-purple-400">{job.id}</span>
            <span className="text-muted-foreground ml-3">next: {job.next_run}</span>
          </div>
        ))}

        <button
          onClick={() => trigger.mutate()}
          disabled={trigger.isPending}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-700 text-white text-sm transition-colors disabled:opacity-50"
        >
          {trigger.isPending ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          Trigger Daily Generation Now
        </button>

        {trigger.isSuccess && (
          <p className="text-xs text-green-400">Scheduler triggered successfully.</p>
        )}
      </div>
    </div>
  );
}
