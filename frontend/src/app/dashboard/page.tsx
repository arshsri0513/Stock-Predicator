"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import {
  getStockHistory,
  getStockInfo,
  getPrediction,
  ApiError,
} from "@/lib/api";
import type { StockHistoryResponse, StockInfo, PredictResponse } from "@/lib/types";
import MetricCard from "@/components/MetricCard";
import PredictionCard from "@/components/PredictionCard";
import PriceChart from "@/components/PriceChart";
import CandlestickChart from "@/components/CandlestickChart";
import VolumeChart from "@/components/VolumeChart";
import PredictionChart from "@/components/PredictionChart";

/**
 * Dashboard page -- the main per-stock overview. Reads `ticker` from the
 * URL (e.g. /dashboard?ticker=AAPL) and fetches three independent pieces
 * of data in parallel: company info, price history, and a prediction.
 *
 * Design choice: these three fetches are independent and don't block each
 * other -- if the prediction fails (e.g. no model trained yet for this
 * ticker), the price chart and info should still render. We track loading
 * and error state PER section rather than one global flag, so a failure
 * in one area doesn't blank out the whole page.
 */
export default function DashboardPage() {
  const searchParams = useSearchParams();
  const ticker = searchParams.get("ticker")?.toUpperCase() || "";

  const [info, setInfo] = useState<StockInfo | null>(null);
  const [history, setHistory] = useState<StockHistoryResponse | null>(null);
  const [prediction, setPrediction] = useState<PredictResponse | null>(null);

  const [infoError, setInfoError] = useState<string | null>(null);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [predictionError, setPredictionError] = useState<string | null>(null);

  const [loading, setLoading] = useState(true);
  const [chartView, setChartView] = useState<"line" | "candlestick">("line");

  useEffect(() => {
    if (!ticker) return;

    setLoading(true);
    setInfo(null);
    setHistory(null);
    setPrediction(null);
    setInfoError(null);
    setHistoryError(null);
    setPredictionError(null);

    getStockInfo(ticker)
      .then(setInfo)
      .catch((e) => setInfoError(e instanceof ApiError ? e.detail : "Failed to load company info."));

    getStockHistory(ticker, "6mo")
      .then(setHistory)
      .catch((e) => setHistoryError(e instanceof ApiError ? e.detail : "Failed to load price history."));

    // Prediction is expected to fail with a clear message if no model has
    // been trained for this ticker yet (see app/api/models.py's 404 in
    // Phase 5) -- that's a normal, anticipated state, not a bug, so we
    // surface it as a helpful message rather than a generic error banner.
    getPrediction(ticker, "random_forest")
      .then(setPrediction)
      .catch((e) => setPredictionError(e instanceof ApiError ? e.detail : "Failed to load prediction."))
      .finally(() => setLoading(false));
  }, [ticker]);

  if (!ticker) {
    return (
      <main className="flex min-h-[calc(100vh-3.5rem)] items-center justify-center px-6">
        <p style={{ color: "var(--text-secondary)" }}>
          No ticker specified. Go back to{" "}
          <a href="/" className="underline" style={{ color: "var(--signal-up)" }}>
            Home
          </a>{" "}
          and search for a stock.
        </p>
      </main>
    );
  }

  const latestRow = history?.data[history.data.length - 1];

  return (
    <main className="mx-auto max-w-7xl px-6 py-8">
      {/* Header */}
      <div className="flex items-baseline justify-between">
        <div>
          <h1 className="font-mono-data text-3xl font-bold">{ticker}</h1>
          {info && <p style={{ color: "var(--text-secondary)" }}>{info.name}</p>}
          {infoError && (
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
              {infoError}
            </p>
          )}
        </div>
        {latestRow && (
          <div className="font-mono-data text-right text-2xl font-semibold">
            ${latestRow.Close.toFixed(2)}
          </div>
        )}
      </div>

      {/* Price chart */}
      <div className="mt-6">
        {historyError ? (
          <ErrorBanner message={historyError} />
        ) : history ? (
          <>
            <div className="mb-2 flex justify-end gap-2">
              <ToggleButton active={chartView === "line"} onClick={() => setChartView("line")}>
                Line
              </ToggleButton>
              <ToggleButton active={chartView === "candlestick"} onClick={() => setChartView("candlestick")}>
                Candlestick
              </ToggleButton>
            </div>
            {chartView === "line" ? (
              <PriceChart data={history.data} />
            ) : (
              <CandlestickChart data={history.data} />
            )}
            <div className="mt-3">
              <VolumeChart data={history.data} />
            </div>
          </>
        ) : (
          <ChartSkeleton />
        )}
      </div>

      {/* Key metrics + prediction */}
      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
        {latestRow && (
          <>
            <MetricCard label="Volume" value={latestRow.Volume.toLocaleString()} />
            <MetricCard
              label="Day Range"
              value={`$${latestRow.Low.toFixed(2)} - $${latestRow.High.toFixed(2)}`}
            />
            <MetricCard
              label="Open"
              value={`$${latestRow.Open.toFixed(2)}`}
            />
          </>
        )}
      </div>

      <div className="mt-6">
        <h2 className="mb-3 text-sm font-medium uppercase tracking-wide" style={{ color: "var(--text-secondary)" }}>
          Prediction
        </h2>
        {predictionError ? (
          <div
            className="rounded-lg border p-4 text-sm"
            style={{ borderColor: "var(--border-subtle)", color: "var(--text-secondary)" }}
          >
            {predictionError}{" "}
            <a href="/predict" className="underline" style={{ color: "var(--signal-up)" }}>
              Train a model
            </a>{" "}
            for {ticker} first.
          </div>
        ) : prediction ? (
          <>
            <PredictionCard prediction={prediction} currentPrice={latestRow?.Close} />
            {history && (
              <div className="mt-3">
                <PredictionChart history={history.data} prediction={prediction} />
              </div>
            )}
          </>
        ) : loading ? (
          <CardSkeleton />
        ) : null}
      </div>
    </main>
  );
}

function ErrorBanner({ message }: { message: string }) {
  return (
    <div
      className="rounded-lg border p-4 text-sm"
      style={{ borderColor: "var(--signal-down)", color: "var(--signal-down)" }}
    >
      {message}
    </div>
  );
}

function ToggleButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className="rounded px-3 py-1 text-xs font-medium transition-colors"
      style={{
        backgroundColor: active ? "var(--bg-elevated)" : "transparent",
        color: active ? "var(--text-primary)" : "var(--text-secondary)",
        border: "1px solid var(--border-subtle)",
      }}
    >
      {children}
    </button>
  );
}

function ChartSkeleton() {
  return (
    <div
      className="h-72 animate-pulse rounded-lg border"
      style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border-subtle)" }}
    />
  );
}

function CardSkeleton() {
  return (
    <div
      className="h-32 animate-pulse rounded-lg border"
      style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border-subtle)" }}
    />
  );
}
