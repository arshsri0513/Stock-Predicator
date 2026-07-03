"use client";
import { formatCurrency } from "@/lib/format";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

import { Holding } from "@/lib/portfolio";

interface Props {
  holdings: Holding[];
}

const COLORS = [
  "#10b981",
  "#3b82f6",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
  "#06b6d4",
  "#84cc16",
  "#f97316",
];

export default function PortfolioAllocationChart({
  holdings,
}: Props) {
  const grouped = holdings.reduce(
    (acc, holding) => {
      const ticker = holding.ticker;

      acc[ticker] =
        (acc[ticker] ?? 0) +
        (holding.market_value ?? 0);

      return acc;
    },
    {} as Record<string, number>
  );

  const data = Object.entries(grouped).map(
    ([name, value]) => ({
      name,
      value,
    })
  );

  if (data.length === 0) {
    return (
      <div
        className="rounded-2xl border p-8"
        style={{
          backgroundColor: "var(--bg-surface)",
          borderColor: "var(--border-subtle)",
        }}
      >
        <h2 className="text-xl font-bold">
          Portfolio Allocation
        </h2>

        <p
          className="mt-4"
          style={{ color: "var(--text-secondary)" }}
        >
          Add holdings to view your allocation chart.
        </p>
      </div>
    );
  }

  return (
    <div
      className="rounded-2xl border p-6"
      style={{
        backgroundColor: "var(--bg-surface)",
        borderColor: "var(--border-subtle)",
      }}
    >
      <h2 className="mb-6 text-2xl font-bold">
        Portfolio Allocation
      </h2>

      <ResponsiveContainer
        width="100%"
        height={350}
      >
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            outerRadius={120}
            label={({ name, percent }) =>
              `${name} ${((percent ?? 0) * 100).toFixed(0)}%`
            }
          >
            {data.map((_, index) => (
              <Cell
                key={index}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Pie>

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

          <Legend
            verticalAlign="bottom"
            height={40}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}