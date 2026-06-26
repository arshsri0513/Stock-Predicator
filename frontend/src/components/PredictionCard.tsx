import type { PredictResponse } from "@/lib/types";

/**
 * Displays a single model's prediction result, including a plain-language
 * framing of what the number means -- per the design skill's guidance to
 * write from the end user's side of the screen, not the system's.
 */

interface PredictionCardProps {
  prediction: PredictResponse;
  currentPrice?: number;
}

export default function PredictionCard({ prediction, currentPrice }: PredictionCardProps) {
  const modelLabel = prediction.model_type
    .split("_")
    .map((w) => w[0].toUpperCase() + w.slice(1))
    .join(" ");

  const diff = currentPrice != null ? prediction.predicted_close - currentPrice : null;
  const diffPercent = currentPrice != null ? (diff! / currentPrice) * 100 : null;
  const trend = diff == null ? "neutral" : diff > 0 ? "up" : diff < 0 ? "down" : "neutral";

  return (
    <div
      className="rounded-lg border p-5"
      style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border-subtle)" }}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wide" style={{ color: "var(--text-secondary)" }}>
          {modelLabel}
        </span>
        <span className="text-xs" style={{ color: "var(--text-secondary)" }}>
          based on {prediction.based_on_date}
        </span>
      </div>

      <div className="font-mono-data mt-2 text-3xl font-bold">
        ${prediction.predicted_close.toFixed(2)}
      </div>

      {diffPercent != null && (
        <div
          className="font-mono-data mt-1 text-sm font-medium"
          style={{ color: trend === "up" ? "var(--signal-up)" : "var(--signal-down)" }}
        >
          {diff! > 0 ? "+" : ""}
          {diffPercent.toFixed(2)}% vs. last close
        </div>
      )}
    </div>
  );
}
