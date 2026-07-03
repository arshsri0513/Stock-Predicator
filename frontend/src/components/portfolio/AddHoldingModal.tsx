"use client";

import { useState } from "react";

interface Props {
  open: boolean;
  onClose: () => void;
  onAdd: (
    ticker: string,
    quantity: number,
    purchasePrice: number
  ) => Promise<void>;
}

export default function AddHoldingModal({
  open,
  onClose,
  onAdd,
}: Props) {
  const [ticker, setTicker] = useState("");
  const [quantity, setQuantity] = useState("");
  const [purchasePrice, setPurchasePrice] = useState("");

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
      <div
        className="w-full max-w-md rounded-2xl border p-6"
        style={{
          backgroundColor: "var(--bg-surface)",
          borderColor: "var(--border-subtle)",
        }}
      >
        <h2 className="text-2xl font-bold">
          Add Holding
        </h2>

        <input
          className="mt-6 w-full rounded-lg border px-4 py-3 bg-transparent"
          placeholder="Ticker (AAPL)"
          value={ticker}
          onChange={(e) => setTicker(e.target.value.toUpperCase())}
        />

        <input
          className="mt-4 w-full rounded-lg border px-4 py-3 bg-transparent"
          placeholder="Quantity"
          type="number"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
        />

        <input
          className="mt-4 w-full rounded-lg border px-4 py-3 bg-transparent"
          placeholder="Purchase Price"
          type="number"
          value={purchasePrice}
          onChange={(e) => setPurchasePrice(e.target.value)}
        />

        <div className="mt-6 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="rounded-lg border px-4 py-2"
          >
            Cancel
          </button>

          <button
            onClick={async () => {
              await onAdd(
                ticker,
                Number(quantity),
                Number(purchasePrice)
              );

              setTicker("");
              setQuantity("");
              setPurchasePrice("");

              onClose();
            }}
            className="rounded-lg bg-emerald-500 px-4 py-2 text-black font-semibold"
          >
            Add
          </button>
        </div>
      </div>
    </div>
  );
}