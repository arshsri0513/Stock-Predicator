"use client";

import { useEffect, useMemo, useState } from "react";

import {
  Holding,
  getPortfolio,
  addHolding,
  removeHolding,
} from "@/lib/portfolio";

import PortfolioSummary from "@/components/portfolio/PortfolioSummary";
import PortfolioTable from "@/components/portfolio/PortfolioTable";
import AddHoldingModal from "@/components/portfolio/AddHoldingModal";

export default function PortfolioPage() {
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [modalOpen, setModalOpen] = useState(false);

  async function loadPortfolio() {
    try {
      const data = await getPortfolio();
      setHoldings(data);
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    loadPortfolio();
  }, []);

  const invested = useMemo(
    () =>
      holdings.reduce(
        (sum, h) => sum + h.purchase_price * h.quantity,
        0
      ),
    [holdings]
  );

  const marketValue = useMemo(
    () =>
      holdings.reduce(
        (sum, h) => sum + (h.market_value ?? 0),
        0
      ),
    [holdings]
  );

  const gainLoss = marketValue - invested;

  return (
    <main className="mx-auto max-w-7xl px-6 py-8">

      <div className="flex items-center justify-between">

        <div>
          <h1 className="text-4xl font-bold">
            💼 Portfolio
          </h1>

          <p
            className="mt-3"
            style={{
              color: "var(--text-secondary)",
            }}
          >
            Track your investments, profit & loss,
            and portfolio performance.
          </p>
        </div>

        <button
          onClick={() => setModalOpen(true)}
          className="rounded-xl px-5 py-3 font-semibold"
          style={{
            backgroundColor: "var(--signal-up)",
            color: "black",
          }}
        >
          + Add Holding
        </button>

      </div>

      <div className="mt-8">
        <PortfolioSummary
          holdings={holdings.length}
          invested={invested}
          marketValue={marketValue}
          gainLoss={gainLoss}
        />
      </div>

      <div className="mt-8">
        <PortfolioTable
          holdings={holdings}
          onRemove={async (id) => {
            try {
              await removeHolding(id);
              await loadPortfolio();
            } catch (err) {
              console.error(err);
              alert("Unable to remove holding.");
            }
          }}
        />
      </div>

      <AddHoldingModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onAdd={async (
          ticker,
          quantity,
          purchasePrice
        ) => {
          try {
            await addHolding({
              ticker,
              quantity,
              purchase_price: purchasePrice,
            });

            await loadPortfolio();
          } catch (err) {
            console.error(err);
            alert("Unable to add holding.");
          }
        }}
      />

    </main>
  );
}