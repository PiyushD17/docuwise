import React, { FormEvent, useMemo, useRef, useState } from "react";
import Spinner from "../components/Spinner";
import ErrorAlert from "../components/ErrorAlert";

type QueryResponse = {
  answer: string;
  sources?: Array<{ title: string; url?: string }>;
};

function errorMessage(e: unknown, fallback = "Something went wrong. Please try again.") {
  if (e instanceof Error) return e.message;
  if (typeof e === "string") return e;
  return fallback;
}

export default function AskPage() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [lastQuestion, setLastQuestion] = useState<string | null>(null);

  // Keep an AbortController handy in case you later add "Cancel" functionality.
  const inFlight = useRef<AbortController | null>(null);

  const canSubmit = useMemo(() => question.trim().length > 0 && !loading, [question, loading]);

  async function submitQuery(q: string) {
    setLoading(true);
    setError(null);
    setAnswer(null);

    const controller = new AbortController();
    inFlight.current = controller;

    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
        signal: controller.signal,
      });

      // Handle non-200s cleanly
      if (!res.ok) {
        let msg = `Request failed (${res.status})`;
        try {
          const data: unknown = await res.json();
          if (data && typeof data === "object") {
            const obj = data as Record<string, unknown>;
            const err = typeof obj.error === "string" ? obj.error : undefined;
            const msgField = typeof obj.message === "string" ? obj.message : undefined;
            msg = err ?? msgField ?? msg;
          }
        } catch {
          /* noop – fallback to default msg */
        }
        throw new Error(msg);
      }

      const data = (await res.json()) as QueryResponse;
      setAnswer(data);
      setLastQuestion(q);
    } catch (e: unknown) {
      if ((e as { name?: string })?.name === "AbortError") return; // ignore if you later add cancel
      setError(errorMessage(e));
    } finally {
      setLoading(false);
      inFlight.current = null;
    }
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!canSubmit) return; // prevents duplicate submits while loading
    await submitQuery(question.trim());
  }

  function retry() {
    if (lastQuestion) submitQuery(lastQuestion);
  }

  return (
    <main className="mx-auto max-w-3xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight">Ask your documents</h1>
        <p className="mt-1 text-sm text-gray-600">
          Type a question about your uploaded files. We’ll wire this to retrieval/LLM in later weeks.
        </p>
      </header>

      <section className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
        <form onSubmit={handleSubmit} className="flex flex-col gap-3" aria-busy={loading}>
          <label htmlFor="question" className="text-sm font-medium text-gray-800">
            Your question
          </label>

          <textarea
            id="question"
            name="question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g., Summarize the main clauses across my uploaded contracts"
            className="min-h-[88px] w-full rounded-xl border border-gray-300 bg-white p-3 text-sm shadow-sm outline-none focus:border-gray-400 focus:ring-2 focus:ring-gray-200 disabled:bg-gray-100"
            disabled={loading}
            aria-disabled={loading}
          />

          <div className="flex items-center justify-between">
            <div className="text-xs text-gray-500">
              {loading ? "Submitting…" : "Tip: Reference filenames for more precise answers."}
            </div>

            <button
              type="submit"
              disabled={!canSubmit}
              className="inline-flex items-center gap-2 rounded-xl bg-gray-900 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-black disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading && <Spinner />}
              {loading ? "Asking…" : "Ask"}
            </button>
          </div>
        </form>

        {/* Error State */}
        {error && (
          <div className="mt-4">
            <ErrorAlert
              message={error}
              onRetry={lastQuestion ? retry : undefined}
              onDismiss={() => setError(null)}
            />
          </div>
        )}

        {/* Answer / Result */}
        {answer && (
          <div className="mt-6 rounded-xl border border-gray-200 bg-gray-50 p-4" aria-live="polite">
            <h2 className="mb-2 text-sm font-semibold text-gray-800">Answer</h2>
            <p className="whitespace-pre-wrap text-sm text-gray-900">{answer.answer}</p>

            {Array.isArray(answer.sources) && answer.sources.length > 0 && (
              <div className="mt-3">
                <h3 className="text-xs font-semibold uppercase tracking-wide text-gray-600">Sources</h3>
                <ul className="mt-1 list-inside list-disc text-sm text-gray-800">
                  {answer.sources.map((s, i) => (
                    <li key={i}>
                      {s.url ? (
                        <a className="underline hover:no-underline" target="_blank" rel="noreferrer" href={s.url}>
                          {s.title}
                        </a>
                      ) : (
                        s.title
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </section>
    </main>
  );
}
