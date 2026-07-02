"use client";

import { useState } from "react";

interface AddStockModalProps {
  open: boolean;
  onClose: () => void;
  onAdd: (ticker: string) => void;
}

export default function AddStockModal({
  open,
  onClose,
  onAdd,
}: AddStockModalProps) {
  const [ticker, setTicker] = useState("");

  if (!open) return null;

  function handleSubmit() {
    if (!ticker.trim()) return;

    onAdd(ticker.toUpperCase());

    setTicker("");

    onClose();
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">

      <div
        className="w-full max-w-md rounded-2xl border p-8"
        style={{
          backgroundColor: "var(--bg-surface)",
          borderColor: "var(--border-subtle)",
        }}
      >

        <h2 className="text-2xl font-bold">
          Add Stock
        </h2>

        <p
          className="mt-2"
          style={{
            color: "var(--text-secondary)",
          }}
        >
          Enter a stock ticker symbol.
        </p>

        <input
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          placeholder="AAPL"
          className="mt-6 w-full rounded-xl border px-4 py-3 outline-none"
          style={{
            backgroundColor: "var(--bg-elevated)",
            borderColor: "var(--border-subtle)",
          }}
        />

        <div className="mt-8 flex justify-end gap-3">

          <button
            onClick={onClose}
            className="rounded-xl border px-5 py-3"
            style={{
              borderColor: "var(--border-subtle)",
            }}
          >
            Cancel
          </button>

          <button
            onClick={handleSubmit}
            className="rounded-xl px-5 py-3 font-semibold"
            style={{
              backgroundColor: "var(--signal-up)",
              color: "black",
            }}
          >
            Add
          </button>

        </div>

      </div>

    </div>
  );
}