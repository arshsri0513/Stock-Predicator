"use client";

import { useTheme } from "next-themes";

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();

  return (
    <main className="mx-auto max-w-6xl px-6 py-8">

      <h1 className="text-4xl font-bold">
        ⚙️ Settings
      </h1>

      <p
        className="mt-2"
        style={{ color: "var(--text-secondary)" }}
      >
        Customize your StockPredict AI experience.
      </p>

      <div className="mt-10 space-y-8">

        {/* ---------------- Appearance ---------------- */}

        <div
          className="rounded-2xl border p-6"
          style={{
            backgroundColor: "var(--bg-surface)",
            borderColor: "var(--border-subtle)",
          }}
        >
          <h2 className="text-2xl font-bold">
            Appearance
          </h2>

          <p
            className="mt-2"
            style={{ color: "var(--text-secondary)" }}
          >
            Select your preferred theme.
          </p>

          <div className="mt-8 grid gap-6 md:grid-cols-3">

            {/* Light */}

            <button
              onClick={() => setTheme("light")}
              className={`rounded-2xl border p-6 text-left transition-all hover:scale-[1.02] ${
                theme === "light" ? "ring-2 ring-green-500" : ""
              }`}
              style={{
                backgroundColor: "var(--bg-base)",
                borderColor: "var(--border-subtle)",
              }}
            >
              <div className="text-5xl">☀️</div>

              <h3 className="mt-5 text-xl font-bold">
                Light
              </h3>

              <p
                className="mt-3 text-sm"
                style={{ color: "var(--text-secondary)" }}
              >
                Bright appearance for daytime use.
              </p>
            </button>

            {/* Dark */}

            <button
              onClick={() => setTheme("dark")}
              className={`rounded-2xl border p-6 text-left transition-all hover:scale-[1.02] ${
                theme === "dark" ? "ring-2 ring-green-500" : ""
              }`}
              style={{
                backgroundColor: "var(--bg-base)",
                borderColor: "var(--border-subtle)",
              }}
            >
              <div className="text-5xl">🌙</div>

              <h3 className="mt-5 text-xl font-bold">
                Dark
              </h3>

              <p
                className="mt-3 text-sm"
                style={{ color: "var(--text-secondary)" }}
              >
                Comfortable for night-time use.
              </p>
            </button>

            {/* System */}

            <button
              onClick={() => setTheme("system")}
              className={`rounded-2xl border p-6 text-left transition-all hover:scale-[1.02] ${
                theme === "system" ? "ring-2 ring-green-500" : ""
              }`}
              style={{
                backgroundColor: "var(--bg-base)",
                borderColor: "var(--border-subtle)",
              }}
            >
              <div className="text-5xl">💻</div>

              <h3 className="mt-5 text-xl font-bold">
                System
              </h3>

              <p
                className="mt-3 text-sm"
                style={{ color: "var(--text-secondary)" }}
              >
                Automatically follows your operating system.
              </p>
            </button>

          </div>
        </div>

        {/* ---------------- Currency ---------------- */}

        <div
          className="rounded-2xl border p-6"
          style={{
            backgroundColor: "var(--bg-surface)",
            borderColor: "var(--border-subtle)",
          }}
        >
          <h2 className="text-2xl font-bold">
            Currency
          </h2>

          <select
            className="mt-5 rounded-lg border px-4 py-3"
            style={{
              backgroundColor: "var(--bg-base)",
              borderColor: "var(--border-subtle)",
              color: "var(--text-primary)",
            }}
          >
            <option>USD ($)</option>
            <option>INR (₹)</option>
            <option>EUR (€)</option>
          </select>
        </div>

        {/* ---------------- Notifications ---------------- */}

        <div
          className="rounded-2xl border p-6"
          style={{
            backgroundColor: "var(--bg-surface)",
            borderColor: "var(--border-subtle)",
          }}
        >
          <h2 className="text-2xl font-bold">
            Notifications
          </h2>

          <div className="mt-6 space-y-4">

            <label className="flex items-center gap-3">
              <input type="checkbox" defaultChecked />
              Email Alerts
            </label>

            <label className="flex items-center gap-3">
              <input type="checkbox" defaultChecked />
              Browser Notifications
            </label>

            <label className="flex items-center gap-3">
              <input type="checkbox" />
              Telegram Notifications
            </label>

          </div>
        </div>

      </div>

    </main>
  );
}