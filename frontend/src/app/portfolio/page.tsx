"use client";

import { useEffect, useMemo, useState } from "react";

import {
  Holding,
  getPortfolio,
  addHolding,
  removeHolding,
  updateHolding,
} from "@/lib/portfolio";

import PortfolioSummary from "@/components/portfolio/PortfolioSummary";
import PortfolioInsights from "@/components/portfolio/PortfolioInsights";
import PortfolioAllocationChart from "@/components/portfolio/PortfolioAllocationChart";
import PortfolioPerformanceChart from "@/components/portfolio/PortfolioPerformanceChart";
import PortfolioTable from "@/components/portfolio/PortfolioTable";
import AddHoldingModal from "@/components/portfolio/AddHoldingModal";
import EditHoldingModal from "@/components/portfolio/EditHoldingModal";

export default function PortfolioPage() {
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [selectedHolding, setSelectedHolding] = useState<Holding | null>(null); 

  async function loadPortfolio() {
      console.log("🔄 Refresh button clicked"); 
    try {
      const data = await getPortfolio();
      console.log("Portfolio data:", data); 
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

        <div className="flex gap-3">

  <button
    onClick={loadPortfolio}
    className="rounded-xl border px-5 py-3"
    style={{
      borderColor: "var(--border-subtle)",
    }}
  >
    🔄 Refresh
  </button>

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
  <PortfolioInsights
    holdings={holdings}
  />
</div>

      <div className="mt-8 grid gap-8 lg:grid-cols-2">

 <PortfolioTable
  holdings={holdings}
  onEdit={(holding) => {
    setSelectedHolding(holding);
    setEditOpen(true);
  }}
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

  <PortfolioAllocationChart
    holdings={holdings}
  />

</div>
<div className="mt-8">
  <PortfolioPerformanceChart
    holdings={holdings}
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

setModalOpen(false);
await loadPortfolio();
          } catch (err) {
            console.error(err);
            alert("Unable to add holding.");
          }
        }}
      />
<EditHoldingModal
  open={editOpen}
  holding={selectedHolding}
  onClose={() => {
    setEditOpen(false);
    setSelectedHolding(null);
  }}
  onSave={async (quantity, purchasePrice) => {
    if (!selectedHolding) return;

    try {
      await updateHolding(selectedHolding.id, {
        quantity,
        purchase_price: purchasePrice,
      });

      setEditOpen(false);
      setSelectedHolding(null);
      await loadPortfolio();
    } catch (err) {
      console.error(err);
      alert("Unable to update holding.");
    }
  }}
/>
    </main>
  );
}