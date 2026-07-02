export default function MarketsPage() {
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
          style={{ color: "var(--text-secondary)" }}
        >
          Explore live stock markets, top gainers, losers, trending stocks,
          and market performance.
        </p>
      </div>

      <div className="mt-8 grid gap-6 md:grid-cols-4">

        {[
          "Top Gainers",
          "Top Losers",
          "Most Active",
          "Trending",
        ].map((item) => (
          <div
            key={item}
            className="rounded-2xl border p-6"
            style={{
              backgroundColor: "var(--bg-surface)",
              borderColor: "var(--border-subtle)",
            }}
          >
            <h2 className="text-xl font-semibold">
              {item}
            </h2>

            <p
              className="mt-3"
              style={{ color: "var(--text-secondary)" }}
            >
              Coming soon...
            </p>
          </div>
        ))}

      </div>

    </main>
  );
}