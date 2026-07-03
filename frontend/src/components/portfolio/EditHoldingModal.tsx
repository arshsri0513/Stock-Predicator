"use client";

import { useEffect, useState } from "react";
import { Holding } from "@/lib/portfolio";

interface Props {
  open: boolean;
  holding: Holding | null;
  onClose: () => void;
  onSave: (
    quantity: number,
    purchasePrice: number
  ) => Promise<void>;
}

export default function EditHoldingModal({
  open,
  holding,
  onClose,
  onSave,
}: Props) {
  const [quantity, setQuantity] = useState("");
  const [purchasePrice, setPurchasePrice] = useState("");

  useEffect(() => {
    if (holding) {
      setQuantity(String(holding.quantity));
      setPurchasePrice(String(holding.purchase_price));
    }
  }, [holding]);

  if (!open || !holding) return null;

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
          Edit Holding
        </h2>

        <input
          className="mt-6 w-full rounded-lg border px-4 py-3 bg-transparent"
          type="number"
          placeholder="Quantity"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
        />

        <input
          className="mt-4 w-full rounded-lg border px-4 py-3 bg-transparent"
          type="number"
          placeholder="Purchase Price"
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
              await onSave(
                Number(quantity),
                Number(purchasePrice)
              );
            }}
            className="rounded-lg bg-blue-500 px-4 py-2 text-white font-semibold"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}