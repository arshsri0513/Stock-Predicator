interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  trend?: "up" | "down" | "neutral";
}

const PREFIX_UNITS = new Set(["$", "€", "£", "¥"]);

export default function MetricCard({
  label,
  value,
  unit,
  trend = "neutral",
}: MetricCardProps) {
  const trendColor =
    trend === "up"
      ? "var(--signal-up)"
      : trend === "down"
      ? "var(--signal-down)"
      : "var(--text-primary)";

  const trendIcon =
    trend === "up"
      ? "▲"
      : trend === "down"
      ? "▼"
      : "●";

  const isPrefix = unit && PREFIX_UNITS.has(unit);

  return (
    <div
      className="group rounded-2xl border p-5 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl"
      style={{
        backgroundColor: "var(--bg-surface)",
        borderColor: "var(--border-subtle)",
      }}
    >
      <div className="flex items-center justify-between">

        <p
          className="text-xs uppercase tracking-[0.18em]"
          style={{
            color: "var(--text-secondary)",
          }}
        >
          {label}
        </p>

        <span
          className="text-sm font-bold"
          style={{
            color: trendColor,
          }}
        >
          {trendIcon}
        </span>

      </div>

      <div
        className="mt-5 font-mono-data text-3xl font-bold transition-transform duration-300 group-hover:scale-105"
        style={{
          color: trendColor,
        }}
      >
        {isPrefix && unit}
        {value}
        {unit && !isPrefix && unit}
      </div>

      <div
        className="mt-5 h-1 rounded-full"
        style={{
          background:
            trend === "up"
              ? "linear-gradient(to right,#10b981,#34d399)"
              : trend === "down"
              ? "linear-gradient(to right,#ef4444,#f87171)"
              : "linear-gradient(to right,#64748b,#94a3b8)",
        }}
      />
    </div>
  );
}