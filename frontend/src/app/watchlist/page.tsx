"use client";
import { addToWatchlist } from "@/lib/watchlist";
import { getStockInfo } from "@/lib/api";
import AddStockModal from "@/components/watchlist/AddStockModal";
import { useEffect, useState } from "react";
import { getWatchlist } from "@/lib/watchlist";

interface WatchlistStock {
  ticker: string;
  company: string;
}

export default function WatchlistPage() {
 const [stocks, setStocks] = useState<WatchlistStock[]>([]);
  const [modalOpen, setModalOpen] = useState(false);

  async function loadWatchlist() {
  try {
    const watchlist = await getWatchlist();

    const stockDetails = await Promise.all(
      watchlist.map(async (item) => {
        const info = await getStockInfo(item.ticker);

        return {
          ticker: info.symbol,
          company: info.name,
        };
      })
    );

    setStocks(stockDetails);
  } catch (error) {
    console.error("Failed to load watchlist:", error);
  }
} 
    useEffect(() => {
  loadWatchlist();
}, []);

  return (
    <main className="mx-auto max-w-6xl px-6 py-8">

      {/* Header */}

      <div className="flex items-center justify-between">

        <div>

          <h1 className="text-4xl font-bold">
            ⭐ My Watchlist
          </h1>

          <p
            className="mt-2"
            style={{ color: "var(--text-secondary)" }}
          >
            Track your favourite stocks in one place.
          </p>

        </div>

     <button
  onClick={() => setModalOpen(true)}
  className="rounded-xl px-5 py-3 font-semibold transition hover:opacity-90"
  style={{
    backgroundColor: "var(--signal-up)",
    color: "black",
  }}
>
  + Add Stock
</button>
         

      </div>

      {/* Table */}

      <div
        className="mt-8 rounded-2xl border overflow-hidden"
        style={{
          borderColor: "var(--border-subtle)",
        }}
      >

        {stocks.map((stock) => (

          <div
            key={stock.ticker}
            className="flex items-center justify-between border-b px-6 py-5 last:border-none"
            style={{
              borderColor: "var(--border-subtle)",
            }}
          >

            <div>

              <h2 className="text-xl font-semibold">
                {stock.ticker}
              </h2>

              <p
                style={{
                  color: "var(--text-secondary)",
                }}
              >
                {stock.company}
              </p>

            </div>

            <a
              href={`/dashboard?ticker=${stock.ticker}`}
              className="rounded-lg border px-4 py-2 text-sm transition hover:opacity-80"
              style={{
                borderColor: "var(--border-subtle)",
              }}
            >
              View →
            </a>

          </div>

        ))}

      </div>
<AddStockModal
  open={modalOpen}
  onClose={() => setModalOpen(false)}
  onAdd={async (ticker) => {
  try {
    await addToWatchlist(ticker);

    await loadWatchlist();

    setModalOpen(false);
  } catch (error) {
    console.error(error);
    alert("Unable to add stock.");
  }
}}
/>
    </main>
  );
}