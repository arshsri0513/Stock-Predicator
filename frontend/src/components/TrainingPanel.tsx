import type { ClassicalModelType } from "@/lib/types";

const MODEL_OPTIONS: { value: ClassicalModelType; label: string }[] = [
  { value: "random_forest", label: "Random Forest" },
  { value: "linear_regression", label: "Linear Regression" },
  { value: "xgboost", label: "XGBoost" },
];

const PERIOD_OPTIONS = ["1y", "2y", "5y"];

interface TrainingPanelProps {
  ticker: string;
  setTicker: (value: string) => void;
  modelType: ClassicalModelType;
  setModelType: (value: ClassicalModelType) => void;
  period: string;
  setPeriod: (value: string) => void;
  training: boolean;
}

export default function TrainingPanel({
  ticker,
  setTicker,
  modelType,
  setModelType,
  period,
  setPeriod,
  training,
}: TrainingPanelProps) {
  return (
    <div
      className="mt-6 rounded-2xl border p-8"
      style={{
        backgroundColor: "var(--bg-surface)",
        borderColor: "var(--border-subtle)",
      }}
    >
      <h2 className="text-2xl font-bold">
        Model Configuration
      </h2>

      <p
        className="mt-2"
        style={{ color: "var(--text-secondary)" }}
      >
        Configure the model and historical data before training.
      </p>

      <div className="mt-8 grid gap-6 md:grid-cols-3">

        {/* Ticker */}

        <div>
          <label className="mb-2 block text-sm font-medium">
            Stock Ticker
          </label>

          <input
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            placeholder="AAPL"
            className="w-full rounded-xl border px-4 py-3 outline-none"
            style={{
              backgroundColor: "var(--bg-elevated)",
              borderColor: "var(--border-subtle)",
            }}
          />
        </div>

        {/* Model */}

        <div>
          <label className="mb-2 block text-sm font-medium">
            ML Model
          </label>

          <select
            value={modelType}
            onChange={(e) =>
              setModelType(e.target.value as ClassicalModelType)
            }
            className="w-full rounded-xl border px-4 py-3 outline-none"
            style={{
              backgroundColor: "var(--bg-elevated)",
              borderColor: "var(--border-subtle)",
            }}
          >
            {MODEL_OPTIONS.map((item) => (
              <option
                key={item.value}
                value={item.value}
              >
                {item.label}
              </option>
            ))}
          </select>
        </div>

        {/* Period */}

        <div>
          <label className="mb-2 block text-sm font-medium">
            Historical Data
          </label>

          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="w-full rounded-xl border px-4 py-3 outline-none"
            style={{
              backgroundColor: "var(--bg-elevated)",
              borderColor: "var(--border-subtle)",
            }}
          >
            {PERIOD_OPTIONS.map((item) => (
              <option
                key={item}
                value={item}
              >
                {item}
              </option>
            ))}
          </select>
        </div>

      </div>

      <button
        type="submit"
        disabled={training}
        className="mt-8 w-full rounded-xl py-4 text-lg font-semibold transition hover:opacity-90 disabled:opacity-60"
        style={{
          backgroundColor: "var(--signal-up)",
          color: "black",
        }}
      >
        {training
          ? "Training Model..."
          : "Train & Predict"}
      </button>
    </div>
  );
}