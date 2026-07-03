import { Holding } from "@/lib/portfolio";
import { formatCurrency } from "@/lib/format";

interface Props {
  holdings: Holding[];
  onRemove: (id: string) => void;
}

export default function PortfolioTable({
  holdings,
  onRemove,
}: Props) {
  if (holdings.length === 0) {
    return (
      <div
        className="rounded-2xl border p-8 text-center"
        style={{
          backgroundColor: "var(--bg-surface)",
          borderColor: "var(--border-subtle)",
        }}
      >
        <h2 className="text-2xl font-semibold">
          No Holdings
        </h2>

        <p
          className="mt-3"
          style={{ color: "var(--text-secondary)" }}
        >
          Add your first stock to start tracking your portfolio.
        </p>
      </div>
    );
  }

  return (
    <div
      className="overflow-x-auto rounded-2xl border"
      style={{
        backgroundColor: "var(--bg-surface)",
        borderColor: "var(--border-subtle)",
      }}
    >
      <table className="w-full">
        <thead>
          <tr
            className="border-b"
            style={{
              borderColor: "var(--border-subtle)",
            }}
          >
            <th className="px-4 py-3 text-left">
              Ticker
            </th>

            <th className="px-4 py-3 text-center">
              Qty
            </th>

            <th className="px-4 py-3 text-right">
              Buy Price
            </th>

            <th className="px-4 py-3 text-right">
              Current
            </th>

            <th className="px-4 py-3 text-right">
              Market Value
            </th>

            <th className="px-4 py-3 text-right">
              Gain / Loss
            </th>

            <th className="px-4 py-3 text-center">
            </th>
          </tr>
        </thead>

        <tbody>
          {holdings.map((holding) => (
            <tr
              key={holding.id}
              className="border-b last:border-none"
              style={{
                borderColor: "var(--border-subtle)",
              }}
            >
              <td className="px-4 py-4 font-semibold">
                {holding.ticker}
              </td>

              <td className="px-4 py-4 text-center">
                {holding.quantity}
              </td>

              <td className="whitespace-nowrap px-4 py-4 text-right">
                {formatCurrency(holding.purchase_price)}
              </td>

              <td className="whitespace-nowrap px-4 py-4 text-right">
                {holding.current_price != null
                  ? formatCurrency(holding.current_price)
                  : "-"}
              </td>

              <td className="whitespace-nowrap px-4 py-4 text-right">
                {holding.market_value != null
                  ? formatCurrency(holding.market_value)
                  : "-"}
              </td>

              <td
                className={`whitespace-nowrap px-4 py-4 text-right font-semibold ${
                  (holding.gain_loss ?? 0) >= 0
                    ? "text-green-400"
                    : "text-red-400"
                }`}
              >
                {holding.gain_loss != null
                  ? `${holding.gain_loss >= 0 ? "+" : "-"}${formatCurrency(
                      Math.abs(holding.gain_loss)
                    )}`
                  : "-"}
              </td>

              <td className="px-4 py-4 text-center">
                <button
                  onClick={() => onRemove(holding.id)}
                  className="rounded-lg border border-red-500 px-3 py-1.5 text-sm text-red-400 transition hover:bg-red-500 hover:text-white"
                >
                  Remove
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}