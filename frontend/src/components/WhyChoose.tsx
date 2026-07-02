export default function WhyChoose() {
  const features = [
    {
      icon: "📈",
      title: "Real-Time Market Data",
      description:
        "Access live stock prices and historical trends for informed investment decisions.",
    },
    {
      icon: "🤖",
      title: "AI Stock Prediction",
      description:
        "Predict future stock prices using Machine Learning and Deep Learning models.",
    },
    {
      icon: "📊",
      title: "Technical Indicators",
      description:
        "Analyze RSI, EMA, SMA, MACD, Bollinger Bands and more technical indicators.",
    },
    {
      icon: "📰",
      title: "News Sentiment",
      description:
        "Analyze financial news and understand market sentiment using AI.",
    },
  ];

  return (
    <section className="py-24 px-6">
      <div className="mx-auto max-w-7xl">

        <div className="text-center">

          <h2 className="text-4xl font-bold">
            Why Choose{" "}
            <span style={{ color: "var(--accent-primary)" }}>
              StockPredict?
            </span>
          </h2>

          <p
            className="mx-auto mt-5 max-w-3xl text-lg"
            style={{ color: "var(--text-secondary)" }}
          >
            Everything you need to analyze stocks, forecast prices, and make
            smarter investment decisions—all in one intelligent platform.
          </p>

        </div>

        <div className="mt-16 grid gap-8 md:grid-cols-2 lg:grid-cols-4">

          {features.map((item) => (
            <div
              key={item.title}
              className="rounded-2xl border p-8 transition-all duration-300 hover:-translate-y-2 hover:shadow-xl"
              style={{
                borderColor: "var(--border-subtle)",
              }}
            >
              <div className="text-5xl">
                {item.icon}
              </div>

              <h3 className="mt-6 text-xl font-semibold">
                {item.title}
              </h3>

              <p
                className="mt-4 leading-7"
                style={{
                  color: "var(--text-secondary)",
                }}
              >
                {item.description}
              </p>
            </div>
          ))}

        </div>

      </div>
    </section>
  );
}