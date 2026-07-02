export default function PortfolioPage() {
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
          💼 Portfolio
        </h1>

        <p
          className="mt-3"
          style={{ color: "var(--text-secondary)" }}
        >
          Track your investments, profit & loss, and portfolio performance.
        </p>
      </div>

    </main>
  );
}