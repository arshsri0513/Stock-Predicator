"use client";

import { useState, FormEvent } from "react";
import { useSearchParams } from "next/navigation";
import { trainModel, getPrediction, ApiError } from "@/lib/api";
import type { ClassicalModelType, TrainResponse, PredictResponse } from "@/lib/types";
import MetricCard from "@/components/MetricCard";
import PredictionCard from "@/components/PredictionCard";

/**
 * Prediction page -- lets a person train a classical model for a ticker
 * and immediately see both the training metrics and a live prediction.
 *
 * This intentionally only exposes the THREE classical models (Phase 5),
 * not the deep learning ones (Phase 6) -- DL training takes 1-5 minutes
 * (see app/api/models.py's /train-dl docstring), which is too long for a
 * synchronous "click and wait" UI. Exposing DL training here would need
 * the background job pattern Phase 13 introduces; until then, scoping
 * this page to fast classical models keeps the experience honest about
 * what it can do quickly.
 */

const MODEL_OPTIONS: { value: ClassicalModelType; label: string }[] = [
  { value: "random_forest", label: "Random Forest" },
  { value: "linear_regression", label: "Linear Regression" },
  { value: "xgboost", label: "XGBoost" },
];

const PERIOD_OPTIONS = ["1y", "2y", "5y"];

export default function PredictPage() {
  const searchParams = useSearchParams();
  const initialTicker = searchParams.get("ticker")?.toUpperCase() || "";

  const [ticker, setTicker] = useState(initialTicker);
  const [modelType, setModelType] = useState<ClassicalModelType>("random_forest");
  const [period, setPeriod] = useState("2y");

  const [training, setTraining] = useState(false);
  const [trainResult, setTrainResult] = useState<TrainResponse | null>(null);
  const [prediction, setPrediction] = useState<PredictResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!ticker.trim()) return;

    setTraining(true);
    setError(null);
    setTrainResult(null);
    setPrediction(null);

    try {
      const result = await trainModel(ticker.trim().toUpperCase(), modelType, period);
      setTrainResult(result);

      // Once training succeeds, immediately fetch a live prediction from
      // the freshly-trained model -- one action, two useful results.
      const pred = await getPrediction(ticker.trim().toUpperCase(), modelType);
      setPrediction(pred);
    } catch (e) {
      setError(e instanceof ApiError ? e.detail : "Training failed. Please try again.");
    } finally {
      setTraining(false);
    }
  }

  return (
    <main className="mx-auto max-w-4xl px-6 py-8">
      <h1 className="text-2xl font-bold">Train &amp; Predict</h1>
      <p className="mt-1 text-sm" style={{ color: "var(--text-secondary)" }}>
        Train a classical ML model on real historical data, then get an instant prediction.
      </p>

      <form onSubmit={handleSubmit} className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-4">
        <div className="sm:col-span-2">
          <label className="mb-1 block text-xs font-medium uppercase tracking-wide" style={{ color: "var(--text-secondary)" }}>
            Ticker
          </label>
          <input
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            placeholder="AAPL"
            className="font-mono-data w-full rounded-md border px-3 py-2 text-sm outline-none"
            style={{ backgroundColor: "var(--bg-elevated)", borderColor: "var(--border-subtle)", color: "var(--text-primary)" }}
          />
        </div>

        <div>
          <label className="mb-1 block text-xs font-medium uppercase tracking-wide" style={{ color: "var(--text-secondary)" }}>
            Model
          </label>
          <select
            value={modelType}
            onChange={(e) => setModelType(e.target.value as ClassicalModelType)}
            className="w-full rounded-md border px-3 py-2 text-sm outline-none"
            style={{ backgroundColor: "var(--bg-elevated)", borderColor: "var(--border-subtle)", color: "var(--text-primary)" }}
          >
            {MODEL_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-xs font-medium uppercase tracking-wide" style={{ color: "var(--text-secondary)" }}>
            History
          </label>
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="w-full rounded-md border px-3 py-2 text-sm outline-none"
            style={{ backgroundColor: "var(--bg-elevated)", borderColor: "var(--border-subtle)", color: "var(--text-primary)" }}
          >
            {PERIOD_OPTIONS.map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </div>

        <div className="sm:col-span-4">
          <button
            type="submit"
            disabled={training}
            className="rounded-md px-5 py-2.5 text-sm font-semibold transition-opacity hover:opacity-90 disabled:opacity-50"
            style={{ backgroundColor: "var(--signal-up)", color: "var(--bg-base)" }}
          >
            {training ? "Training... (10-30s)" : "Train & Predict"}
          </button>
        </div>
      </form>

      {error && (
        <div
          className="mt-6 rounded-lg border p-4 text-sm"
          style={{ borderColor: "var(--signal-down)", color: "var(--signal-down)" }}
        >
          {error}
        </div>
      )}

      {trainResult && (
        <div className="mt-8">
          <h2 className="mb-3 text-sm font-medium uppercase tracking-wide" style={{ color: "var(--text-secondary)" }}>
            Training Results ({trainResult.rows_trained_on} rows)
          </h2>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <MetricCard label="RMSE" value={trainResult.metrics.rmse} unit="$" />
            <MetricCard label="MAE" value={trainResult.metrics.mae} unit="$" />
            <MetricCard label="MAPE" value={trainResult.metrics.mape} unit="%" />
            <MetricCard
              label="R² Score"
              value={trainResult.metrics.r2_score}
              trend={trainResult.metrics.r2_score > 0.5 ? "up" : trainResult.metrics.r2_score > 0 ? "neutral" : "down"}
            />
          </div>
        </div>
      )}

      {prediction && (
        <div className="mt-8">
          <h2 className="mb-3 text-sm font-medium uppercase tracking-wide" style={{ color: "var(--text-secondary)" }}>
            Latest Prediction
          </h2>
          <PredictionCard prediction={prediction} />
        </div>
      )}
    </main>
  );
}
