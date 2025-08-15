import React from "react";

type Source = { title?: string; url?: string };
type QueryResponse = { answer?: string; sources?: Source[]; error?: string };

export default function AskPage() {
  const [q, setQ] = React.useState("");
  const [answer, setAnswer] = React.useState<string | null>(null);
  const [sources, setSources] = React.useState<Source[] | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [err, setErr] = React.useState<string | null>(null);

  async function onAsk(e: React.FormEvent) {
    e.preventDefault();
    if (!q.trim()) return;

    setLoading(true);
    setErr(null);
    setAnswer(null);
    setSources(null);

    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });

      const ct = res.headers.get("content-type") || "";
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }
      if (!ct.includes("application/json")) {
        throw new Error("Unexpected response from server");
      }

      const data: QueryResponse = await res.json();
      if (data.error) throw new Error(data.error);

      setAnswer(data.answer || "(no answer)");
      setSources(Array.isArray(data.sources) ? data.sources : null);
    } catch (e: any) {
      setErr(e?.message || "Query failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <h1 className="text-xl font-semibold">Ask your documents</h1>
      <p className="mt-1 text-sm text-gray-600">Type a question about your uploaded files.</p>

      <form onSubmit={onAsk} className="mt-4 space-y-3">
        <textarea
          value={q}
          onChange={(e) => setQ(e.target.value)}
          rows={4}
          placeholder="e.g., Summarize the key points of the latest PDF"
          className="w-full resize-none rounded-md border px-3 py-2 text-sm outline-none focus:border-indigo-500"
        />
        <div className="flex items-center gap-2">
          <button
            type="submit"
            disabled={!q.trim() || loading}
            className={`rounded-md px-4 py-2 text-sm font-medium text-white ${
              !q.trim() || loading ? "bg-gray-400" : "bg-indigo-600 hover:bg-indigo-500"
            }`}
          >
            {loading ? "Thinking…" : "Ask"}
          </button>
        </div>
      </form>

      <div className="mt-4 space-y-3">
        {loading && (
          <div className="inline-flex items-center gap-2 text-sm text-gray-700">
            <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
            </svg>
            <span>Working on it…</span>
          </div>
        )}

        {err && <p className="text-sm text-red-700">Error: {err}</p>}

        {answer && !loading && (
          <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3">
            <p className="text-sm text-gray-900 whitespace-pre-wrap">{answer}</p>
          </div>
        )}

        {sources && sources.length > 0 && (
          <div className="rounded-lg border bg-gray-50 p-3">
            <p className="text-xs font-medium text-gray-700">Sources</p>
            <ul className="mt-2 space-y-1">
              {sources.map((s, i) => (
                <li key={i} className="text-xs text-gray-700">
                  {s.url ? (
                    <a href={s.url} target="_blank" rel="noreferrer" className="underline hover:text-gray-900">
                      {s.title || s.url}
                    </a>
                  ) : (
                    <span>{s.title || "Untitled source"}</span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
