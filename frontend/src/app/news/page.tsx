"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { getNews, ApiError } from "@/lib/api";
import type { NewsResponse } from "@/lib/types";

/**
 * News page -- displays recent headlines scored by both VADER and FinBERT
 * (Phase 7). We show both scores side by side deliberately, rather than
 * picking one as "the" sentiment -- Phase 7's own testing showed they
 * frequently disagree, and hiding that disagreement would misrepresent
 * how reliable either signal really is.
 *
 * SUSPENSE WRAPPER (Phase 15): see dashboard/page.tsx for the full
 * explanation.
 */
export default function NewsPage() {
  return (
    <Suspense fallback={null}>
      <NewsContent />
    </Suspense>
  );
}

function NewsContent() {
  const searchParams = useSearchParams();
  const initialTicker = searchParams.get("ticker")?.toUpperCase() || "";

  const [ticker, setTicker] = useState(initialTicker);
  const [inputValue, setInputValue] = useState(initialTicker);
  const [data, setData] = useState<NewsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!ticker) return;
    setLoading(true);
    setError(null);
    setData(null);
    getNews(ticker, 10)
      .then(setData)
      .catch((e) => setError(e instanceof ApiError ? e.detail : "Failed to load news."))
      .finally(() => setLoading(false));
  }, [ticker]);

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (inputValue.trim()) setTicker(inputValue.trim().toUpperCase());
  }

  return (
    <main className="mx-auto max-w-3xl px-6 py-8">
      <h1 className="text-2xl font-bold">News &amp; Sentiment</h1>
      <p className="mt-1 text-sm" style={{ color: "var(--text-secondary)" }}>
        Recent headlines scored with VADER (fast, general-purpose) and FinBERT (finance-specific).
      </p>

      <form onSubmit={handleSearch} className="mt-6 flex gap-2">
        <input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="AAPL"
          className="font-mono-data w-48 rounded-md border px-3 py-2 text-sm outline-none"
          style={{ backgroundColor: "var(--bg-elevated)", borderColor: "var(--border-subtle)", color: "var(--text-primary)" }}
        />
        <button
          type="submit"
          className="rounded-md px-4 py-2 text-sm font-semibold transition-opacity hover:opacity-90"
          style={{ backgroundColor: "var(--signal-up)", color: "var(--bg-base)" }}
        >
          Load
        </button>
      </form>

      {loading && (
        <p className="mt-6 text-sm" style={{ color: "var(--text-secondary)" }}>
          Loading headlines and scoring sentiment -- the first request after server
          startup can take 30-90 seconds while FinBERT loads.
        </p>
      )}

      {error && (
        <div className="mt-6 rounded-lg border p-4 text-sm" style={{ borderColor: "var(--signal-down)", color: "var(--signal-down)" }}>
          {error}
        </div>
      )}

      {data && !loading && (
        <div className="mt-6 space-y-3">
          <div className="text-xs" style={{ color: "var(--text-secondary)" }}>
            {data.article_count} articles &middot; average VADER score:{" "}
            <span className="font-mono-data" style={{ color: sentimentColor(data.average_vader_compound) }}>
              {data.average_vader_compound.toFixed(3)}
            </span>
          </div>

          {data.articles.map((article, i) => (
            <a
              key={i}
              href={article.link}
              target="_blank"
              rel="noopener noreferrer"
              className="block rounded-lg border p-4 transition-colors hover:opacity-90"
              style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border-subtle)" }}
            >
              <div className="text-sm font-medium">{article.title}</div>
              <div className="mt-1 text-xs" style={{ color: "var(--text-secondary)" }}>
                {article.publisher}
              </div>
              <div className="mt-2 flex gap-3 text-xs">
                <span style={{ color: sentimentColor(article.vader_compound) }}>
                  VADER: {article.vader_label}
                </span>
                <span style={{ color: "var(--text-secondary)" }}>
                  FinBERT: {article.finbert_label} ({(article.finbert_confidence * 100).toFixed(0)}%)
                </span>
              </div>
            </a>
          ))}
        </div>
      )}
    </main>
  );
}

function sentimentColor(score: number): string {
  if (score > 0.05) return "var(--signal-up)";
  if (score < -0.05) return "var(--signal-down)";
  return "var(--text-secondary)";
}
