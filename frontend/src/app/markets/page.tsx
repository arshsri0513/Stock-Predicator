"use client";

import { useEffect, useState } from "react";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface MarketStock {
  ticker: string;
  price: number;
  change_percent: number;
}

interface MarketResponse {
  gainers: MarketStock[];
  losers: MarketStock[];
}

export default function MarketsPage() {
  const [data, setData] = useState<MarketResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const res = await fetch(`${API_BASE}/market/movers`);

        if (!res.ok) {
          throw new Error("Failed to load market data.");
        }

        const json = await res.json();
        setData(json);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  function MarketCard({
    title,
    stocks,
  }: {
    title: string;
    stocks: MarketStock[];
  }) {
    return (
      <div
        className="rounded-2xl border p-6"
        style={{
          backgroundColor: "var(--bg-surface)",
          borderColor: "var(--border-subtle)",
        }}
      >
        <h2 className="mb-5 text-xl font-semibold">{title}</h2>

        {stocks.length === 0 ? (
          <p style={{ color: "var(--text-secondary)" }}>
            No data available.
          </p>
        ) : (
          <div className="space-y-4">
            {stocks.map((stock) => (
              <div
                key={stock.ticker}
                className="flex items-center justify-between"
              >
                <div>
                  <div className="font-semibold">
                    {stock.ticker}
                  </div>

                  <div
                    className="text-sm"
                    style={{
                      color: "var(--text-secondary)",
                    }}
                  >
                    ${stock.price}
                  </div>
                </div>

                <div
                  className="font-semibold"
                  style={{
                    color:
                      stock.change_percent >= 0
                        ? "var(--signal-up)"
                        : "var(--signal-down)",
                  }}
                >
                  {stock.change_percent > 0 ? "+" : ""}
                  {stock.change_percent.toFixed(2)}%
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <main className="mx-auto max-w-7xl px-6 py-8">
      <div
        className="rounded-2xl border p-8"
        style={{
          backgroundColor: "var(--bg-surface)",
          borderColor: "var(--border-subtle)",
        }}
      >
        <h1 className="text-4xl font-bold">
          📈 Markets
        </h1>

        <p
          className="mt-3 text-lg"
          style={{
            color: "var(--text-secondary)",
          }}
        >
          Live market movers powered by Finnhub.
        </p>
      </div>

      {loading ? (
        <div className="mt-8 text-center">
          Loading market data...
        </div>
      ) : (
        <div className="mt-8 grid gap-6 md:grid-cols-2">
          <MarketCard
            title="🚀 Top Gainers"
            stocks={data?.gainers ?? []}
          />

          <MarketCard
            title="📉 Top Losers"
            stocks={data?.losers ?? []}
          />
        </div>
      )}
    </main>
  );
}