export default function Models() {
  const models = [
    {
      name: "Random Forest",
      description:
        "An ensemble learning algorithm that combines multiple decision trees to improve prediction accuracy and reduce overfitting.",
      color: "from-green-500 to-emerald-600",
      badge: "Traditional ML",
    },
    {
      name: "LSTM",
      description:
        "Long Short-Term Memory networks capture long-term dependencies in stock price sequences for time-series forecasting.",
      color: "from-blue-500 to-cyan-600",
      badge: "Deep Learning",
    },
    {
      name: "Technical Analysis",
      description:
        "RSI, EMA, SMA, MACD, Bollinger Bands and other indicators provide valuable insights into market trends.",
      color: "from-purple-500 to-pink-600",
      badge: "Indicators",
    },
    {
      name: "News Sentiment",
      description:
        "Financial news is analyzed using Natural Language Processing to estimate market sentiment and improve predictions.",
      color: "from-orange-500 to-red-500",
      badge: "NLP",
    },
  ];

  return (
    <section className="py-24 px-6">
      <div className="mx-auto max-w-7xl">

        <div className="text-center">

          <h2 className="text-4xl font-bold">
            Machine Learning{" "}
            <span style={{ color: "var(--accent-primary)" }}>
              Models
            </span>
          </h2>

          <p
            className="mx-auto mt-5 max-w-3xl text-lg"
            style={{ color: "var(--text-secondary)" }}
          >
            StockPredict combines Machine Learning, Deep Learning,
            Technical Analysis and Natural Language Processing to
            deliver intelligent stock market predictions.
          </p>

        </div>

        <div className="mt-16 grid gap-8 md:grid-cols-2">

          {models.map((model) => (

            <div
              key={model.name}
              className="overflow-hidden rounded-2xl border transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl"
              style={{
                borderColor: "var(--border-subtle)",
              }}
            >

              <div
                className={`bg-gradient-to-r ${model.color} p-6`}
              >

                <span className="rounded-full bg-white/20 px-3 py-1 text-sm font-semibold">
                  {model.badge}
                </span>

                <h3 className="mt-5 text-3xl font-bold text-white">
                  {model.name}
                </h3>

              </div>

              <div className="p-6">

                <p
                  className="leading-8"
                  style={{
                    color: "var(--text-secondary)",
                  }}
                >
                  {model.description}
                </p>

              </div>

            </div>

          ))}

        </div>

      </div>
    </section>
  );
}