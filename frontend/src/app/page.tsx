import SearchBar from "@/components/SearchBar";

/**
 * Home page -- the entry point. Deliberately sparse: this is a tool, not a
 * marketing site, so the job of this page is to get a ticker symbol typed
 * in and get out of the way, not to sell the product with hero imagery.
 */
export default function HomePage() {
  return (
    <main className="flex min-h-[calc(100vh-3.5rem)] flex-col items-center justify-center px-6">
      <div className="w-full max-w-md text-center">
        <h1 className="font-mono-data text-sm font-medium tracking-widest" style={{ color: "var(--text-secondary)" }}>
          STOCKPREDICT
        </h1>
        <p className="mt-3 text-2xl font-semibold">
          Look up a stock to begin.
        </p>
        <p className="mt-2 text-sm" style={{ color: "var(--text-secondary)" }}>
          Live prices, technical indicators, ML/DL predictions, and news sentiment.
        </p>

        <div className="mt-8 flex justify-center">
          <SearchBar />
        </div>

        <div className="mt-10 flex flex-wrap justify-center gap-2">
          {["AAPL", "TSLA", "MSFT", "NVDA"].map((ticker) => (
            <a
              key={ticker}
              href={`/dashboard?ticker=${ticker}`}
              className="font-mono-data rounded-md border px-3 py-1.5 text-xs transition-colors hover:opacity-80"
              style={{ borderColor: "var(--border-subtle)", color: "var(--text-secondary)" }}
            >
              {ticker}
            </a>
          ))}
        </div>
      </div>
    </main>
  );
}
