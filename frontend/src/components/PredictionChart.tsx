"use client";

import {
  ComposedChart,
  Line,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import type { OHLCVRow, PredictResponse } from "@/lib/types";

/**
 * Shows the last N days of real closing prices as a line, with the
 * model's predicted next price plotted as a separate point one step
 * ahead -- making it visually obvious whether the prediction continues
 * the recent trend or breaks from it, which a bare number on its own
 * can't communicate.
 */

interface PredictionChartProps {
  history: OHLCVRow[];
  prediction: PredictResponse;
}

export default function PredictionChart({ history, prediction }: PredictionChartProps) {
  const recent = history.slice(-30); // last 30 days for a readable, focused view

  // Build a single combined series where actual prices use the `actual`
  // key and only the final, synthetic "next day" point has a `predicted`
  // key -- Recharts draws two independent lines/series from the same
  // underlying array by reading different keys per point.
  const chartData = [
    ...recent.map((row) => ({ date: row.Date, actual: row.Close, predicted: null as number | null })),
    { date: prediction.based_on_date + " (predicted)", actual: null, predicted: prediction.predicted_close },
  ];

  return (
    <div
      className="rounded-lg border p-4"
      style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border-subtle)" }}
    >
      <ResponsiveContainer width="100%" height={260}>
        <ComposedChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 10, fill: "var(--text-secondary)" }}
            tickFormatter={(v: string) => v.slice(5, 10)}
            minTickGap={50}
            axisLine={{ stroke: "var(--border-subtle)" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "var(--text-secondary)" }}
            domain={["auto", "auto"]}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v: number) => `$${v.toFixed(0)}`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--bg-elevated)",
              border: "1px solid var(--border-subtle)",
              borderRadius: 8,
              fontSize: 12,
            }}
            labelStyle={{ color: "var(--text-secondary)" }}
            formatter={(value, name) => [
              typeof value === "number" ? `$${value.toFixed(2)}` : "—",
              name === "actual" ? "Actual" : "Predicted",
            ]}
          />
          <Line
            type="monotone"
            dataKey="actual"
            stroke="var(--signal-up)"
            strokeWidth={1.5}
            dot={false}
            connectNulls={false}
            name="actual"
          />
          <Scatter dataKey="predicted" fill="var(--accent)" name="predicted" />
        </ComposedChart>
      </ResponsiveContainer>
      <div className="mt-2 flex gap-4 text-xs" style={{ color: "var(--text-secondary)" }}>
        <span><span style={{ color: "var(--signal-up)" }}>—</span> Actual close</span>
        <span><span style={{ color: "var(--accent)" }}>●</span> Predicted next close</span>
      </div>
    </div>
  );
}
