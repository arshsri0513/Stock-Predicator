import type { PredictResponse } from "@/lib/types";

interface PredictionCardProps {
  prediction: PredictResponse;
  currentPrice?: number;
}

export default function PredictionCard({
  prediction,
  currentPrice,
}: PredictionCardProps) {
  const modelLabel = prediction.model_type
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");

  const diff =
    currentPrice != null
      ? prediction.predicted_close - currentPrice
      : null;

  const diffPercent =
    currentPrice != null
      ? (diff! / currentPrice) * 100
      : null;

  const trend =
    diff == null
      ? "neutral"
      : diff > 0
      ? "up"
      : diff < 0
      ? "down"
      : "neutral";

  const recommendation =
    diffPercent == null
      ? "HOLD"
      : diffPercent > 2
      ? "BUY"
      : diffPercent < -2
      ? "SELL"
      : "HOLD";

  const recommendationColor =
    recommendation === "BUY"
      ? "var(--signal-up)"
      : recommendation === "SELL"
      ? "var(--signal-down)"
      : "#f59e0b";

  return (
    <div
      className="rounded-2xl border p-8"
      style={{
        backgroundColor: "var(--bg-surface)",
        borderColor: "var(--border-subtle)",
      }}
    >
      {/* Header */}

      <div className="flex items-center justify-between">

        <div>

          <p
            className="text-sm uppercase tracking-[0.2em]"
            style={{
              color: "var(--text-secondary)",
            }}
          >
            AI Prediction
          </p>

          <h2 className="mt-2 text-3xl font-bold">
            {modelLabel}
          </h2>

        </div>

        <span
          className="rounded-full px-4 py-2 text-sm font-semibold"
          style={{
            backgroundColor: "rgba(16,185,129,0.15)",
            color: "var(--signal-up)",
          }}
        >
          Active
        </span>

      </div>

      {/* Price */}

      <div className="mt-10 grid gap-6 md:grid-cols-2">

        <div>

          <p
            className="text-sm"
            style={{
              color: "var(--text-secondary)",
            }}
          >
            Predicted Price
          </p>

          <h1 className="mt-2 font-mono-data text-5xl font-bold">
            ${prediction.predicted_close.toFixed(2)}
          </h1>

        </div>

        {currentPrice != null && (

          <div>

            <p
              className="text-sm"
              style={{
                color: "var(--text-secondary)",
              }}
            >
              Current Price
            </p>

            <h2 className="mt-2 font-mono-data text-4xl font-semibold">
              ${currentPrice.toFixed(2)}
            </h2>

          </div>

        )}

      </div>

      {/* Statistics */}

      {diffPercent != null && (

        <div className="mt-10 grid gap-4 md:grid-cols-3">

          <div
            className="rounded-xl border p-5"
            style={{
              borderColor: "var(--border-subtle)",
            }}
          >
            <p
              className="text-sm"
              style={{
                color: "var(--text-secondary)",
              }}
            >
              Expected Change
            </p>

            <h3
              className="mt-2 text-2xl font-bold"
              style={{
                color:
                  trend === "up"
                    ? "var(--signal-up)"
                    : trend === "down"
                    ? "var(--signal-down)"
                    : "var(--text-primary)",
              }}
            >
              {diff! > 0 ? "+" : ""}
              {diffPercent.toFixed(2)}%
            </h3>
          </div>

          <div
            className="rounded-xl border p-5"
            style={{
              borderColor: "var(--border-subtle)",
            }}
          >
            <p
              className="text-sm"
              style={{
                color: "var(--text-secondary)",
              }}
            >
              Recommendation
            </p>

            <h3
              className="mt-2 text-2xl font-bold"
              style={{
                color: recommendationColor,
              }}
            >
              {recommendation}
            </h3>
          </div>

          <div
            className="rounded-xl border p-5"
            style={{
              borderColor: "var(--border-subtle)",
            }}
          >
            <p
              className="text-sm"
              style={{
                color: "var(--text-secondary)",
              }}
            >
              Prediction Date
            </p>

            <h3 className="mt-2 text-lg font-semibold">
              {prediction.based_on_date}
            </h3>
          </div>

        </div>

      )}

    </div>
  );
}