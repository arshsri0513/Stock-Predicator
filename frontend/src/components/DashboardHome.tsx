"use client";
import SearchBar from "@/components/SearchBar";
import { useEffect, useState } from "react";
import {
  getWatchlist,
  getPredictionHistory,
  getAlerts,
} from "@/lib/api";
import { getPortfolio } from "@/lib/portfolio";
import Link from "next/link";

export default function DashboardHome() {
const [watchlistCount, setWatchlistCount] = useState(0);
const [portfolioValue, setPortfolioValue] = useState(0);
const [predictionCount, setPredictionCount] = useState(0);
const [alertCount, setAlertCount] = useState(0);
useEffect(() => {
  async function loadDashboard() {
  try {
    const watchlist = await getWatchlist();
    console.log("WATCHLIST:", watchlist);
    setWatchlistCount(watchlist.length);

    const predictions = await getPredictionHistory();
    console.log("PREDICTIONS:", predictions);
    setPredictionCount(predictions.length);

    const portfolio = await getPortfolio();
    console.log("PORTFOLIO:", portfolio);

    const alerts = await getAlerts();
    console.log("ALERTS:", alerts);
    setAlertCount(alerts.length);

    const total = portfolio.reduce(
      (sum, holding) => sum + (holding.market_value ?? 0),
      0
    );

    console.log("TOTAL PORTFOLIO VALUE:", total);

    setPortfolioValue(total);
  } catch (err) {
    console.error("Dashboard Error:", err);
  }
}

  loadDashboard();
}, []);

const quickAccess = [
  {
    title: "⭐ My Watchlist",
    description: "View and manage your saved stocks.",
    href: "/watchlist",
  },
  {
    title: "📊 Prediction History",
    description: "Review all previous predictions.",
    href: "/predict",
  },
  {
    title: "📈 Portfolio Tracker",
    description: "Manage your investments and holdings.",
    href: "/portfolio",
  },
  {
    title: "🔔 Price Alerts",
    description: "Create and manage stock alerts.",
    href: "/alerts",
  },
  {
    title: "📰 Market News",
    description: "Stay updated with the latest news.",
    href: "/news",
  },
  {
    title: "⚙️ Settings",
    description: "Customize your application.",
    href: "/settings",
  },
];

  return (
    <main className="mx-auto max-w-7xl px-6 py-8">

      {/* Welcome */}

      <div
        className="rounded-2xl border p-8"
        style={{
          backgroundColor: "var(--bg-surface)",
          borderColor: "var(--border-subtle)",
        }}
      >
        <h1 className="text-4xl font-bold">
          Welcome back 👋
        </h1>

        <p
          className="mt-3 text-lg"
          style={{ color: "var(--text-secondary)" }}
        >
          Search any stock, monitor the market, and manage your predictions
          from one intelligent dashboard.
        </p>

        <div className="mt-8 max-w-xl">
          <SearchBar />
        </div>
      </div>

      {/* Quick Stats */}

     <div className="mt-8 grid gap-6 md:grid-cols-4">

        {[
  {
    title: "Watchlist",
    value: watchlistCount.toString(),
    desc: "Saved Stocks",
  },
  {
    title: "Predictions",
    value: predictionCount.toString(),
    desc: "Completed",
  },
  {
    title: "Portfolio",
    value: `$${portfolioValue.toFixed(2)}`,
    desc: "Current Value",
  },
  {
  title: "Alerts",
  value: alertCount.toString(),
  desc: "Active",
  },
].map((item) => (
          <div
            key={item.title}
            className="rounded-2xl border p-6"
            style={{
              backgroundColor: "var(--bg-surface)",
              borderColor: "var(--border-subtle)",
            }}
          >
            <p
              className="text-sm"
              style={{
                color: "var(--text-secondary)",
              }}
            >
              {item.title}
            </p>

            <h2 className="mt-2 text-4xl font-bold">
              {item.value}
            </h2>

            <p
              className="mt-2 text-sm"
              style={{
                color: "var(--text-secondary)",
              }}
            >
              {item.desc}
            </p>
          </div>
        ))}

        </div>   

    <div
  className="mt-8 rounded-2xl border p-8"
  style={{
    backgroundColor: "var(--bg-surface)",
    borderColor: "var(--border-subtle)",
  }}
>
  <h2 className="text-2xl font-bold">
    🚀 Quick Access
  </h2>

  <p
    className="mt-2"
    style={{ color: "var(--text-secondary)" }}
  >
    Quickly jump to the features you use most.
  </p>

  <div className="mt-6 grid gap-5 md:grid-cols-2 lg:grid-cols-3">

    {quickAccess.map((item) => (
      <Link
        key={item.href}
        href={item.href}
        className="rounded-xl border p-5 transition-all hover:scale-[1.02] hover:shadow-lg"
        style={{
          borderColor: "var(--border-subtle)",
          backgroundColor: "var(--bg-base)",
        }}
      >
        <h3 className="text-lg font-semibold">
          {item.title}
        </h3>

        <p
          className="mt-3 text-sm"
          style={{
            color: "var(--text-secondary)",
          }}
        >
          {item.description}
        </p>
      </Link>
    ))}

  </div>
</div>   
    </main>
  );
}