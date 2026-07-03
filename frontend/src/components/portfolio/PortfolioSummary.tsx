import { formatCurrency } from "@/lib/format";

interface Props {
  holdings: number;
  invested: number;
  marketValue: number;
  gainLoss: number;
}

export default function PortfolioSummary({
  holdings,
  invested,
  marketValue,
  gainLoss,
}: Props) {
  const gainPercent =
    invested > 0 ? (gainLoss / invested) * 100 : 0;

  const cards = [
    {
      title: "Holdings",
      value: holdings,
    },
    {
      title: "Invested",
      value: formatCurrency(invested),
    },
    {
      title: "Market Value",
      value: formatCurrency(marketValue),
    },
    {
      title: "Profit / Loss",
      value: `${gainLoss >= 0 ? "+" : "-"}${formatCurrency(
        Math.abs(gainLoss)
      )} (${gainPercent.toFixed(2)}%)`,
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
            style={{ color: "var(--text-secondary)" }}
          >
            {card.title}
          </p>

          <h2
            className={`mt-3 text-3xl font-bold ${
              card.title === "Profit / Loss"
                ? gainLoss >= 0
                  ? "text-green-400"
                  : "text-red-400"
                : ""
            }`}
          >
            {card.value}
          </h2>
        </div>
      ))}
    </div>
  );
}