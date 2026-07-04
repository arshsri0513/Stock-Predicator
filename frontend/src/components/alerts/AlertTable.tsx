"use client";

import { Alert } from "@/lib/api";

interface Props {
  alerts: Alert[];
  onDelete: (id: string) => Promise<void>;
  onCheck: (id: string) => Promise<void>;
}

export default function AlertTable({
  alerts,
  onDelete,
  onCheck,
}: Props) {
  if (alerts.length === 0) {
    return (
      <div
        className="rounded-2xl border p-8 text-center"
        style={{
          backgroundColor: "var(--bg-surface)",
          borderColor: "var(--border-subtle)",
        }}
      >
        <h2 className="text-2xl font-semibold">
          No Alerts
        </h2>

        <p
          className="mt-3"
          style={{ color: "var(--text-secondary)" }}
        >
          Create your first price alert above.
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
            style={{ borderColor: "var(--border-subtle)" }}
          >
            <th className="px-4 py-3 text-left">Ticker</th>
            <th className="px-4 py-3 text-center">Direction</th>
            <th className="px-4 py-3 text-right">Target Price</th>
            <th className="px-4 py-3 text-center">Status</th>
            <th className="px-4 py-3 text-center">Created</th>
            <th className="px-4 py-3 text-center">Actions</th>
          </tr>
        </thead>

        <tbody>
          {alerts.map((alert) => (
            <tr
              key={alert.id}
              className="border-b last:border-none"
              style={{
                borderColor: "var(--border-subtle)",
              }}
            >
              <td className="px-4 py-4 font-semibold">
                {alert.ticker}
              </td>

              <td className="px-4 py-4 text-center">
                {alert.direction.toUpperCase()}
              </td>

              <td className="px-4 py-4 text-right">
                ${alert.threshold_price.toFixed(2)}
              </td>

              <td
                className={`px-4 py-4 text-center font-semibold ${
                  alert.is_active === "true"
                    ? "text-green-400"
                    : "text-red-400"
                }`}
              >
                {alert.is_active === "true"
                  ? "Active"
                  : "Inactive"}
              </td>

              <td className="px-4 py-4 text-center">
                {new Date(alert.created_at).toLocaleDateString()}
              </td>

              <td className="px-4 py-4">
                <div className="flex justify-center gap-2">
                  <button
                    onClick={() => onCheck(alert.id)}
                    className="rounded-lg border px-3 py-1 text-sm"
                    style={{
                      borderColor: "var(--signal-up)",
                      color: "var(--signal-up)",
                    }}
                  >
                    Check
                  </button>

                  <button
                    onClick={() => onDelete(alert.id)}
                    className="rounded-lg border border-red-500 px-3 py-1 text-sm text-red-400 hover:bg-red-500 hover:text-white"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}