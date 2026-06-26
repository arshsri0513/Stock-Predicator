"use client";

import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceLine,
} from "recharts";
import type { IndicatorRow } from "@/lib/types";

/**
 * Three stacked panels, mirroring how real trading platforms lay out
 * technical analysis: main price chart with Bollinger Bands on top, RSI
 * and MACD as smaller panels below sharing the same date axis.
 *
 * Note: early rows have null indicator values (see Phase 4's warm-up
 * period explanation) -- Recharts simply skips null points when drawing
 * lines, which produces the correct visual effect of each indicator line
 * only appearing once it has enough history, with no extra handling
 * needed on our part.
 */

interface IndicatorChartProps {
  data: IndicatorRow[];
}

const tickFormatter = (value: string) => value.slice(5);
const axisStyle = { fontSize: 11, fill: "var(--text-secondary)" };

export default function IndicatorChart({ data }: IndicatorChartProps) {
  return (
    <div className="space-y-4">
      {/* Panel 1: Price + Bollinger Bands */}
      <Panel title="Price & Bollinger Bands" height={260}>
        <ComposedChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" vertical={false} />
          <XAxis dataKey="Date" tick={axisStyle} tickFormatter={tickFormatter} minTickGap={40} axisLine={{ stroke: "var(--border-subtle)" }} tickLine={false} />
          <YAxis tick={axisStyle} domain={["auto", "auto"]} axisLine={false} tickLine={false} tickFormatter={(v) => `$${v.toFixed(0)}`} />
          <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "var(--text-secondary)" }} />
          <Line type="monotone" dataKey="bb_upper" stroke="var(--text-secondary)" strokeWidth={1} strokeDasharray="4 3" dot={false} name="Upper Band" />
          <Line type="monotone" dataKey="Close" stroke="var(--signal-up)" strokeWidth={1.5} dot={false} name="Close" />
          <Line type="monotone" dataKey="bb_lower" stroke="var(--text-secondary)" strokeWidth={1} strokeDasharray="4 3" dot={false} name="Lower Band" />
        </ComposedChart>
      </Panel>

      {/* Panel 2: RSI */}
      <Panel title="RSI (14)" height={140}>
        <ComposedChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" vertical={false} />
          <XAxis dataKey="Date" tick={axisStyle} tickFormatter={tickFormatter} minTickGap={40} axisLine={{ stroke: "var(--border-subtle)" }} tickLine={false} />
          <YAxis tick={axisStyle} domain={[0, 100]} axisLine={false} tickLine={false} ticks={[30, 50, 70]} />
          <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "var(--text-secondary)" }} />
          <ReferenceLine y={70} stroke="var(--signal-down)" strokeDasharray="3 3" />
          <ReferenceLine y={30} stroke="var(--signal-up)" strokeDasharray="3 3" />
          <Line type="monotone" dataKey="rsi_14" stroke="var(--accent)" strokeWidth={1.5} dot={false} name="RSI" />
        </ComposedChart>
      </Panel>

      {/* Panel 3: MACD */}
      <Panel title="MACD" height={140}>
        <ComposedChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" vertical={false} />
          <XAxis dataKey="Date" tick={axisStyle} tickFormatter={tickFormatter} minTickGap={40} axisLine={{ stroke: "var(--border-subtle)" }} tickLine={false} />
          <YAxis tick={axisStyle} domain={["auto", "auto"]} axisLine={false} tickLine={false} />
          <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "var(--text-secondary)" }} />
          <ReferenceLine y={0} stroke="var(--border-subtle)" />
          <Line type="monotone" dataKey="macd_line" stroke="var(--signal-up)" strokeWidth={1.5} dot={false} name="MACD" />
          <Line type="monotone" dataKey="macd_signal" stroke="var(--signal-down)" strokeWidth={1.5} dot={false} name="Signal" />
        </ComposedChart>
      </Panel>
    </div>
  );
}

const tooltipStyle = {
  backgroundColor: "var(--bg-elevated)",
  border: "1px solid var(--border-subtle)",
  borderRadius: 8,
  fontSize: 12,
};

function Panel({ title, height, children }: { title: string; height: number; children: React.ReactElement }) {
  return (
    <div className="rounded-lg border p-4" style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border-subtle)" }}>
      <div className="mb-2 text-xs font-medium uppercase tracking-wide" style={{ color: "var(--text-secondary)" }}>
        {title}
      </div>
      <ResponsiveContainer width="100%" height={height}>
        {children}
      </ResponsiveContainer>
    </div>
  );
}
