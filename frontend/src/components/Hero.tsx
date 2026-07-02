import SearchBar from "@/components/SearchBar";

export default function Hero() {
  return (
    <section className="flex flex-col items-center justify-center px-6 py-16">
      <div className="w-full max-w-5xl text-center">

        {/* Logo */}
        <h1
          className="font-mono-data text-sm font-semibold uppercase tracking-[0.4em]"
          style={{ color: "var(--accent-primary)" }}
        >
          STOCKPREDICT
        </h1>

        {/* Main Heading */}
        <h2 className="mt-6 text-5xl font-extrabold leading-tight md:text-6xl">
          AI-Powered
          <br />
          Stock Prediction Platform
        </h2>

        {/* Description */}
        <p
          className="mx-auto mt-6 max-w-3xl text-lg leading-8"
          style={{ color: "var(--text-secondary)" }}
        >
          Predict future stock prices using Machine Learning and Deep Learning
          models. Analyze live market data, technical indicators, financial
          news sentiment, and interactive charts—all from one intelligent
          dashboard.
        </p>

        {/* Feature Badges */}
        <div className="mt-10 flex flex-wrap justify-center gap-3">
          {[
            "📈 Live Market Data",
            "🤖 AI Prediction",
            "📊 Technical Indicators",
            "📰 News Sentiment",
          ].map((feature) => (
            <span
              key={feature}
              className="rounded-full border px-4 py-2 text-sm transition-all hover:scale-105"
              style={{
                borderColor: "var(--border-subtle)",
                color: "var(--text-secondary)",
              }}
            >
              {feature}
            </span>
          ))}
        </div>

        {/* Search */}
        <div className="mt-10 flex justify-center">
          <SearchBar />
        </div>

        {/* Popular Stocks */}
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          {["AAPL", "TSLA", "MSFT", "NVDA"].map((ticker) => (
            <a
              key={ticker}
              href={`/dashboard?ticker=${ticker}`}
              className="rounded-lg border px-5 py-2 text-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-lg"
              style={{
                borderColor: "var(--border-subtle)",
                color: "var(--text-secondary)",
              }}
            >
              {ticker}
            </a>
          ))}
        </div>

      </div>
    </section>
  );
}