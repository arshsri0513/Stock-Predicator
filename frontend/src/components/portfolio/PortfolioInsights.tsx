import { Holding } from "@/lib/portfolio";
import { formatCurrency } from "@/lib/format";

interface Props {
  holdings: Holding[];
}

export default function PortfolioInsights({
  holdings,
}: Props) {
  if (holdings.length === 0) return null;

  const best = [...holdings].sort(
    (a, b) => (b.gain_loss ?? 0) - (a.gain_loss ?? 0)
  )[0];

  const worst = [...holdings].sort(
    (a, b) => (a.gain_loss ?? 0) - (b.gain_loss ?? 0)
  )[0];

  const largest = [...holdings].sort(
    (a, b) => (b.market_value ?? 0) - (a.market_value ?? 0)
  )[0];

  const avgReturn =
    holdings.reduce(
      (sum, h) => sum + (h.gain_loss_percent ?? 0),
      0
    ) / holdings.length;

  const cards = [
    {
      title: "🏆 Best Performer",
      ticker: best.ticker,
      value: formatCurrency(best.gain_loss ?? 0),
      color: "text-green-400",
    },
    {
      title: "📉 Worst Performer",
      ticker: worst.ticker,
      value: formatCurrency(worst.gain_loss ?? 0),
      color: "text-red-400",
    },
    {
      title: "💰 Largest Position",
      ticker: largest.ticker,
      value: formatCurrency(largest.market_value ?? 0),
      color: "text-cyan-400",
    },
    {
      title: "📊 Average Return",
      ticker: "",
      value: `${avgReturn.toFixed(2)}%`,
      color:
        avgReturn >= 0
          ? "text-green-400"
          : "text-red-400",
    },
  ];

  return (
    <div className="grid gap-6 md:grid-cols-4">
      {cards.map((card) => (
        <div
          key={card.title}
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
            {card.title}
          </p>

          {card.ticker && (
            <h3 className="mt-3 text-xl font-bold">
              {card.ticker}
            </h3>
          )}

          <p
            className={`mt-2 text-2xl font-bold ${card.color}`}
          >
            {card.value}
          </p>
        </div>
      ))}
    </div>
  );
}