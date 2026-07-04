"use client";

import { useState } from "react";

interface Props {
  onCreate: (
    ticker: string,
    thresholdPrice: number,
    direction: "above" | "below"
  ) => Promise<void>;
}

export default function AlertForm({ onCreate }: Props) {
  const [ticker, setTicker] = useState("");
  const [thresholdPrice, setThresholdPrice] = useState("");
  const [direction, setDirection] = useState<"above" | "below">("above");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    if (!ticker || !thresholdPrice) return;

    setLoading(true);

    try {
      await onCreate(
        ticker.toUpperCase(),
        Number(thresholdPrice),
        direction
      );

      setTicker("");
      setThresholdPrice("");
      setDirection("above");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-2xl border p-6"
      style={{
        backgroundColor: "var(--bg-surface)",
        borderColor: "var(--border-subtle)",
      }}
    >
      <h2 className="mb-6 text-2xl font-bold">
        Create Alert
      </h2>

      <div className="grid gap-4 md:grid-cols-3">

        <input
          type="text"
          placeholder="Ticker"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          className="rounded-xl border px-4 py-3"
          style={{
            backgroundColor: "var(--bg-elevated)",
            borderColor: "var(--border-subtle)",
          }}
        />

        <input
          type="number"
          step="0.01"
          placeholder="Threshold Price"
          value={thresholdPrice}
          onChange={(e) => setThresholdPrice(e.target.value)}
          className="rounded-xl border px-4 py-3"
          style={{
            backgroundColor: "var(--bg-elevated)",
            borderColor: "var(--border-subtle)",
          }}
        />

        <select
          value={direction}
          onChange={(e) =>
            setDirection(e.target.value as "above" | "below")
          }
          className="rounded-xl border px-4 py-3"
          style={{
            backgroundColor: "var(--bg-elevated)",
            borderColor: "var(--border-subtle)",
          }}
        >
          <option value="above">Above</option>
          <option value="below">Below</option>
        </select>

      </div>

      <button
        type="submit"
        disabled={loading}
        className="mt-6 rounded-xl px-6 py-3 font-semibold"
        style={{
          backgroundColor: "var(--signal-up)",
          color: "black",
        }}
      >
        {loading ? "Creating..." : "Create Alert"}
      </button>
    </form>
  );
}