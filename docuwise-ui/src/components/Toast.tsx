// src/components/Toast.tsx
"use client";
import React from "react";
import { createPortal } from "react-dom";

type ToastItem = { id: string; message: string; type?: "success" | "error" | "info" };
const ToastContext = React.createContext<{ push: (t: Omit<ToastItem, "id">) => void } | null>(null);

export function useToast() {
  const ctx = React.useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within <ToastProvider/>");
  return ctx;
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<ToastItem[]>([]);
  const [mounted, setMounted] = React.useState(false);
  const [rootEl, setRootEl] = React.useState<HTMLElement | null>(null);

  React.useEffect(() => {
    setMounted(true);
    setRootEl(document.getElementById("toast-root"));
  }, []);

  const push = React.useCallback((t: Omit<ToastItem, "id">) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((prev) => [...prev, { id, ...t }]);
    setTimeout(() => setToasts((prev) => prev.filter((x) => x.id !== id)), 3000);
  }, []);

  return (
    <ToastContext.Provider value={{ push }}>
      {children}
      {/* Render nothing on server and on the client's first paint */}
      {mounted && rootEl
        ? createPortal(
            <div className="fixed inset-x-0 top-3 z-50 mx-auto flex max-w-md flex-col gap-2 px-2">
              {toasts.map((t) => (
                <div
                  key={t.id}
                  className={`rounded-lg border px-3 py-2 text-sm shadow ${
                    t.type === "error"
                      ? "border-red-200 bg-red-50 text-red-700"
                      : t.type === "success"
                      ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                      : "border-gray-200 bg-white text-gray-900"
                  }`}
                >
                  {t.message}
                </div>
              ))}
            </div>,
            rootEl
          )
        : null}
    </ToastContext.Provider>
  );
}
