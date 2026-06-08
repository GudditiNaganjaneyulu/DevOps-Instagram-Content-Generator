"use client";
import { useState, useCallback, useRef } from "react";
import { checkHealth } from "@/lib/api";

export type WakeupStatus = "idle" | "checking" | "warming" | "ready" | "timeout";

const MAX_WAIT_MS = 60_000;
const POLL_INTERVAL_MS = 3_000;

export function useBackendWakeup() {
  const [status, setStatus] = useState<WakeupStatus>("idle");
  const [elapsed, setElapsed] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const clearTimer = () => {
    if (timerRef.current) clearInterval(timerRef.current);
  };

  // Returns true when backend is ready, false on timeout
  const ensureAwake = useCallback(async (): Promise<boolean> => {
    setStatus("checking");
    setElapsed(0);

    try {
      await checkHealth();
      setStatus("ready");
      return true;
    } catch {
      // Backend is cold-starting — poll until it responds
      setStatus("warming");
    }

    return new Promise((resolve) => {
      const start = Date.now();

      timerRef.current = setInterval(async () => {
        const ms = Date.now() - start;
        setElapsed(Math.round(ms / 1000));

        if (ms >= MAX_WAIT_MS) {
          clearTimer();
          setStatus("timeout");
          resolve(false);
          return;
        }

        try {
          await checkHealth();
          clearTimer();
          setStatus("ready");
          resolve(true);
        } catch {
          // still warming, keep polling
        }
      }, POLL_INTERVAL_MS);
    });
  }, []);

  const reset = useCallback(() => {
    clearTimer();
    setStatus("idle");
    setElapsed(0);
  }, []);

  return { status, elapsed, ensureAwake, reset };
}
