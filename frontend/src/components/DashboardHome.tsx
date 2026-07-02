import SearchBar from "@/components/SearchBar";

export default function DashboardHome() {
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
            value: "0",
            desc: "Saved Stocks",
          },
          {
            title: "Predictions",
            value: "0",
            desc: "Completed",
          },
          {
            title: "Portfolio",
            value: "$0",
            desc: "Coming Soon",
          },
          {
            title: "Alerts",
            value: "0",
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

      {/* Coming Soon */}

      <div
        className="mt-8 rounded-2xl border p-8"
        style={{
          backgroundColor: "var(--bg-surface)",
          borderColor: "var(--border-subtle)",
        }}
      >
        <h2 className="text-2xl font-bold">
          🚀 Coming Soon
        </h2>

        <div className="mt-6 grid gap-4 md:grid-cols-2">

          {[
            "⭐ Personal Watchlist",
            "📊 Prediction History",
            "📈 Portfolio Tracker",
            "🔔 Price Alerts",
            "🤖 AI Investment Assistant",
            "📄 PDF Reports",
          ].map((feature) => (
            <div
              key={feature}
              className="rounded-xl border px-5 py-4"
              style={{
                borderColor: "var(--border-subtle)",
              }}
            >
              {feature}
            </div>
          ))}

        </div>
      </div>

    </main>
  );
}