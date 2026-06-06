import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "@/types";
import { setToken, clearToken } from "@/lib/api";

interface AuthState {
  token: string | null;
  user: User | null;
  setAuth: (token: string, user: User) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      setAuth: (token, user) => {
        setToken(token);
        set({ token, user });
      },
      logout: () => {
        clearToken();
        set({ token: null, user: null });
      },
      isAuthenticated: () => !!get().token,
    }),
    { name: "auth-storage", partialize: (s) => ({ token: s.token, user: s.user }) }
  )
);
