/**
 * A single labeled metric, e.g. "RMSE: 14.10" or "Current price: $294.30".
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

export default function MetricCard({ label, value, unit, trend = "neutral" }: MetricCardProps) {
  const trendColor =
    trend === "up" ? "var(--signal-up)" : trend === "down" ? "var(--signal-down)" : "var(--text-primary)";

  return (
    <div
      className="rounded-lg border p-4"
      style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border-subtle)" }}
    >
      <div className="text-xs font-medium uppercase tracking-wide" style={{ color: "var(--text-secondary)" }}>
        {label}
      </div>
      <div className="font-mono-data mt-1.5 text-2xl font-semibold" style={{ color: trendColor }}>
        {value}
        {unit && <span className="ml-1 text-base font-normal">{unit}</span>}
      </div>
    </div>
  );
}
