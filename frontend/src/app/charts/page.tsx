"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { getTechnicalIndicators, ApiError } from "@/lib/api";
import type { TechnicalIndicatorsResponse } from "@/lib/types";
import IndicatorChart from "@/components/IndicatorChart";

/**
 * Charts page -- deeper technical analysis view than the Dashboard's
 * simple price line. Shows price with Bollinger Bands overlaid, plus RSI
 * and MACD as separate panels below, mirroring how real trading platforms
 * stack indicator panels under the main price chart.
 */
export default function ChartsPage() {
  const searchParams = useSearchParams();
  const initialTicker = searchParams.get("ticker")?.toUpperCase() || "";

  const [ticker, setTicker] = useState(initialTicker);
  const [inputValue, setInputValue] = useState(initialTicker);
  const [data, setData] = useState<TechnicalIndicatorsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!ticker) return;
    setLoading(true);
    setError(null);
    getTechnicalIndicators(ticker, "1y")
      .then(setData)
      .catch((e) => setError(e instanceof ApiError ? e.detail : "Failed to load indicators."))
      .finally(() => setLoading(false));
  }, [ticker]);

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (inputValue.trim()) setTicker(inputValue.trim().toUpperCase());
  }

  return (
    <main className="mx-auto max-w-6xl px-6 py-8">
      <h1 className="text-2xl font-bold">Technical Charts</h1>
      <p className="mt-1 text-sm" style={{ color: "var(--text-secondary)" }}>
        Price action with Bollinger Bands, RSI, and MACD.
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

      {!ticker && (
        <p className="mt-8 text-sm" style={{ color: "var(--text-secondary)" }}>
          Enter a ticker above to view its technical charts.
        </p>
      )}

      {error && (
        <div className="mt-6 rounded-lg border p-4 text-sm" style={{ borderColor: "var(--signal-down)", color: "var(--signal-down)" }}>
          {error}
        </div>
      )}

      {loading && (
        <div className="mt-6 h-96 animate-pulse rounded-lg border" style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border-subtle)" }} />
      )}

      {data && !loading && (
        <div className="mt-6">
          <IndicatorChart data={data.data} />
        </div>
      )}
    </main>
  );
}
