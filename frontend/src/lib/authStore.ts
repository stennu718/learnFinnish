import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthState {
  token: string | null;
  setToken: (token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      setToken: (token) => set({ token }),
      logout: () => set({ token: null }),
    }),
    {
      name: "learnfinnish-auth",
      // Store in sessionStorage (cleared when tab closes) instead of localStorage
      // This is more secure than localStorage for JWT tokens
      storage: {
        getItem: (name) => {
          try {
            return sessionStorage.getItem(name);
          } catch {
            return null;
          }
        },
        setItem: (name, value) => {
          try {
            sessionStorage.setItem(name, value);
          } catch {
            // ignore
          }
        },
        removeItem: (name) => {
          try {
            sessionStorage.removeItem(name);
          } catch {
            // ignore
          }
        },
      },
    }
  )
);
