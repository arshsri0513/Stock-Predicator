"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import type { OHLCVRow } from "@/lib/types";

/**
 * Closing price area chart. We use Close only here (not full OHLC
 * candlesticks) deliberately -- Recharts doesn't have a built-in
 * candlestick chart type, and building one from scratch is real extra
 * work for a Phase 11 concern (Visualization), not Phase 10 (basic
 * Dashboard). We'll revisit candlesticks specifically in Phase 11.
 */

interface PriceChartProps {
  data: OHLCVRow[];
}

export default function PriceChart({ data }: PriceChartProps) {
  const chartData = data.map((row) => ({
    date: row.Date,
    close: row.Close,
  }));

  return (
    <div
      className="rounded-lg border p-4"
      style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border-subtle)" }}
    >
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--signal-up)" stopOpacity={0.25} />
              <stop offset="100%" stopColor="var(--signal-up)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: "var(--text-secondary)" }}
            tickFormatter={(value) => value.slice(5)} // "2026-01-15" -> "01-15"
            minTickGap={40}
            axisLine={{ stroke: "var(--border-subtle)" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "var(--text-secondary)" }}
            domain={["auto", "auto"]}
            axisLine={false}
            tickLine={false}
            tickFormatter={(value) => `$${value.toFixed(0)}`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--bg-elevated)",
              border: "1px solid var(--border-subtle)",
              borderRadius: 8,
              fontSize: 12,
            }}
            labelStyle={{ color: "var(--text-secondary)" }}
            formatter={(value: number) => [`$${value.toFixed(2)}`, "Close"]}
          />
          <Area
            type="monotone"
            dataKey="close"
            stroke="var(--signal-up)"
            strokeWidth={1.5}
            fill="url(#priceGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
