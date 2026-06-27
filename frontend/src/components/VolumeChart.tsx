"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import type { OHLCVRow } from "@/lib/types";

/**
 * Volume bar chart, colored green/red by whether that day closed up or
 * down vs its own open -- a standard convention that lets a quick glance
 * connect volume spikes to the price direction that produced them.
 */

interface VolumeChartProps {
  data: OHLCVRow[];
}

export default function VolumeChart({ data }: VolumeChartProps) {
  return (
    <div
      className="rounded-lg border p-4"
      style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border-subtle)" }}
    >
      <div className="mb-2 text-xs font-medium uppercase tracking-wide" style={{ color: "var(--text-secondary)" }}>
        Volume
      </div>
      <ResponsiveContainer width="100%" height={120}>
        <BarChart data={data}>
          <XAxis
            dataKey="Date"
            tick={{ fontSize: 11, fill: "var(--text-secondary)" }}
            tickFormatter={(v: string) => v.slice(5)}
            minTickGap={40}
            axisLine={{ stroke: "var(--border-subtle)" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "var(--text-secondary)" }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v: number) => `${(v / 1_000_000).toFixed(0)}M`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--bg-elevated)",
              border: "1px solid var(--border-subtle)",
              borderRadius: 8,
              fontSize: 12,
            }}
            labelStyle={{ color: "var(--text-secondary)" }}
            formatter={(value: number) => [value.toLocaleString(), "Volume"]}
          />
          <Bar dataKey="Volume" isAnimationActive={false}>
            {data.map((row, i) => (
              <Cell
                key={i}
                fill={row.Close >= row.Open ? "var(--signal-up)" : "var(--signal-down)"}
                fillOpacity={0.7}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
