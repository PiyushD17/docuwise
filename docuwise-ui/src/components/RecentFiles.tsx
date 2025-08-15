"use client";
import React from "react";

type FileItem = {
  id: string;
  filename: string;
  size?: number;
  uploaded_at?: string;
  status?: string;
};

export default function RecentFiles() {
  const [items, setItems] = React.useState<FileItem[] | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    (async () => {
      try {
        const res = await fetch("/api/files?limit=10", { cache: "no-store", headers: { Accept: "application/json" } });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const ct = res.headers.get("content-type") || "";
        if (!ct.includes("application/json")) throw new Error("Unexpected response");
        const data = await res.json();
        const list: FileItem[] = Array.isArray(data) ? data : data.items || [];
        setItems(list);
      } catch (e: any) {
        setError(e?.message || "Failed to load files");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-semibold">Recent uploads</h3>
      <p className="mt-1 text-sm text-gray-600">Latest files you’ve uploaded.</p>

      <div className="mt-4">
        {loading && <p className="text-sm text-gray-600">Loading…</p>}
        {error && <p className="text-sm text-red-700">Couldn’t load files: {error}</p>}
        {!loading && !error && (!items || items.length === 0) && (
          <p className="text-sm text-gray-600">No files yet.</p>
        )}
        {!loading && items && items.length > 0 && (
          <ul className="divide-y">
            {items.map((it) => (
              <li key={it.id} className="flex items-center justify-between py-3">
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium">{it.filename}</p>
                  <p className="truncate text-xs text-gray-600">
                    {typeof it.size === "number" ? `${(it.size / (1024 * 1024)).toFixed(2)} MB` : ""}
                    {it.uploaded_at ? ` • ${new Date(it.uploaded_at).toLocaleString()}` : ""}
                  </p>
                </div>
                <span
                  className={`text-xs ${
                    it.status === "done" ? "text-emerald-700" : it.status === "failed" ? "text-red-700" : "text-gray-700"
                  }`}
                >
                  {it.status || "unknown"}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
