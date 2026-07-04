"use client";

import { useEffect, useState } from "react";

import {
  Alert,
  getAlerts,
  createAlert,
  deleteAlert,
  checkAlert,
} from "@/lib/api";

import AlertForm from "@/components/alerts/AlertForm";
import AlertTable from "@/components/alerts/AlertTable";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  async function loadAlerts() {
    try {
      const data = await getAlerts();
      setAlerts(data);
    } catch (err) {
      console.error(err);
      alert("Unable to load alerts.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAlerts();
  }, []);

  return (
    <main className="mx-auto max-w-7xl px-6 py-8">

      <div className="mb-8">
        <h1 className="text-4xl font-bold">
          🔔 Price Alerts
        </h1>

        <p
          className="mt-3"
          style={{
            color: "var(--text-secondary)",
          }}
        >
          Create price alerts and manually check whether the market has
          reached your target price.
        </p>
      </div>

      <AlertForm
        onCreate={async (
          ticker,
          thresholdPrice,
          direction
        ) => {
          try {
            await createAlert({
              ticker,
              threshold_price: thresholdPrice,
              direction,
            });

            await loadAlerts();
          } catch (err) {
            console.error(err);
            alert("Unable to create alert.");
          }
        }}
      />

      <div className="mt-8">

        {loading ? (
          <div
            className="rounded-2xl border p-8 text-center"
            style={{
              backgroundColor: "var(--bg-surface)",
              borderColor: "var(--border-subtle)",
            }}
          >
            Loading alerts...
          </div>
        ) : (
          <AlertTable
            alerts={alerts}
            onDelete={async (id) => {
              try {
                await deleteAlert(id);
                await loadAlerts();
              } catch (err) {
                console.error(err);
                alert("Unable to delete alert.");
              }
            }}
            onCheck={async (id) => {
              try {
                await checkAlert(id);
                alert("Alert checked successfully.");
              } catch (err) {
                console.error(err);
                alert("Unable to check alert.");
              }
            }}
          />
        )}

      </div>

    </main>
  );
}