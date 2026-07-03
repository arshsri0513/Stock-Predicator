"use client";
import { formatCurrency } from "@/lib/format";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

import { Holding } from "@/lib/portfolio";

interface Props {
  holdings: Holding[];
}

export default function PortfolioPerformanceChart({
  holdings,
}: Props) {
  const data = holdings.map((holding, index) => ({
    name: `${holding.ticker} ${index + 1}`,
    value: holding.market_value ?? 0,
  }));

  return (
    <div
      className="rounded-2xl border p-6"
      style={{
        backgroundColor: "var(--bg-surface)",
        borderColor: "var(--border-subtle)",
      }}
    >
      <h2 className="mb-6 text-2xl font-bold">
        Portfolio Value
      </h2>

      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />

          <XAxis dataKey="name" />

          <YAxis />

          <Tooltip
  formatter={(value) => {
    const numericValue =
      typeof value === "number"
        ? value
        : Number(value ?? 0);

    return [
      formatCurrency(numericValue),
      "Market Value",
    ];
  }}
/>

          <Line
            type="monotone"
            dataKey="value"
            stroke="#10b981"
            strokeWidth={3}
            dot
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}