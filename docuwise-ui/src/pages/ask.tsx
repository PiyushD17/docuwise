import React from "react";
import Spinner from "../components/Spinner";

export default function AskPage() {
  const [q, setQ] = React.useState("");
  const [a, setA] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [err, setErr] = React.useState<string | null>(null);

  async function onAsk(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true); setErr(null); setA(null);
    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setA(data?.answer || "(no answer)");
    } catch (e: any) {
      setErr(e?.message || "Query failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <h1 className="text-xl font-semibold">Ask your documents</h1>
      <form onSubmit={onAsk} className="mt-4 flex items-center gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Type a question…"
          className="w-full rounded-md border px-3 py-2 text-sm outline-none focus:border-indigo-500"
        />
        <button
          type="submit"
          disabled={!q || loading}
          className={`rounded-md px-4 py-2 text-sm font-medium text-white ${!q || loading ? "bg-gray-400" : "bg-indigo-600 hover:bg-indigo-500"}`}
        >
          Ask
        </button>
      </form>
      <div className="mt-4">
        {loading && <Spinner label="Thinking…" />}
        {err && <p className="text-sm text-red-700">{err}</p>}
        {a && !loading && <p className="text-sm text-gray-900">{a}</p>}
      </div>
    </div>
  );
}
