/**
 * A single labeled metric, e.g. "RMSE: $14.10" or "MAPE: 3.39%".
 * Used across Dashboard, Prediction, and Charts pages -- one consistent
 * way to present a number with context, rather than each page inventing
 * its own layout for "label + value."
 */

interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  trend?: "up" | "down" | "neutral";
}

// Units that read naturally BEFORE the number (currency symbols) vs units
// that read naturally AFTER the number (percent, etc). Without this
// distinction, a generic "always append" approach produces "13.95$"
// instead of "$13.95" -- correct character, wrong position, which is what
// actually caused the earlier MAPE/RMSE display oddities (not a missing
// font glyph as initially suspected).
const PREFIX_UNITS = new Set(["$", "€", "£", "¥"]);

export default function MetricCard({ label, value, unit, trend = "neutral" }: MetricCardProps) {
  const trendColor =
    trend === "up" ? "var(--signal-up)" : trend === "down" ? "var(--signal-down)" : "var(--text-primary)";

  const isPrefix = unit && PREFIX_UNITS.has(unit);

  return (
    <div
      className="rounded-lg border p-4"
      style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border-subtle)" }}
    >
      <div className="text-xs font-medium uppercase tracking-wide" style={{ color: "var(--text-secondary)" }}>
        {label}
      </div>
      <div className="font-mono-data mt-1.5 text-2xl font-semibold" style={{ color: trendColor }}>
        {isPrefix && unit}
        {value}
        {unit && !isPrefix && unit}
      </div>
    </div>
  );
}
