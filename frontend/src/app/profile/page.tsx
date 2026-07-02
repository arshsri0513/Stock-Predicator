"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  getMe,
  getWatchlist,
  addToWatchlist,
  removeFromWatchlist,
  ApiError,
} from "@/lib/api";
import type { WatchlistItem } from "@/lib/types";

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<{ id: string; email: string } | null>(null);
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Watchlist form input state
  const [newTicker, setNewTicker] = useState("");
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      setLoading(false);
      return;
    }

    async function loadData() {
      try {
        const userData = await getMe();
        setUser(userData);
        const watchlistData = await getWatchlist();
        setWatchlist(watchlistData);
      } catch (e) {
        setError(e instanceof ApiError ? e.detail : "Failed to load profile data.");
        // If 401 Unauthorized, token is probably invalid, so clear it
        if (e instanceof ApiError && e.status === 401) {
          localStorage.removeItem("token");
          setUser(null);
        }
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!newTicker.trim()) return;

    setActionLoading(true);
    setActionError(null);
    try {
      const addedItem = await addToWatchlist(newTicker.trim().toUpperCase());
      setWatchlist((prev) => [...prev, addedItem]);
      setNewTicker("");
    } catch (e) {
      setActionError(e instanceof ApiError ? e.detail : "Failed to add stock.");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleRemove(ticker: string) {
    setActionLoading(true);
    setActionError(null);
    try {
      await removeFromWatchlist(ticker.toUpperCase());
      setWatchlist((prev) => prev.filter((item) => item.ticker !== ticker.toUpperCase()));
    } catch (e) {
      setActionError(e instanceof ApiError ? e.detail : "Failed to remove stock.");
    } finally {
      setActionLoading(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem("token");
    setUser(null);
    setWatchlist([]);
    window.dispatchEvent(new Event("auth-change"));
    router.push("/login");
  }

  if (loading) {
    return (
      <main className="mx-auto max-w-4xl px-6 py-12 text-center">
        <p style={{ color: "var(--text-secondary)" }}>Loading profile...</p>
      </main>
    );
  }

  // Not logged in UI
  if (!user) {
    return (
      <main className="mx-auto max-w-md px-6 py-16">
        <div
          className="rounded-xl border p-8 text-center shadow-xl"
          style={{
            backgroundColor: "var(--bg-surface)",
            borderColor: "var(--border-subtle)",
          }}
        >
          <div className="font-mono-data text-5xl mb-4" style={{ color: "var(--text-secondary)" }}>
            🔑
          </div>
          <h1 className="text-xl font-bold">Authentication Required</h1>
          <p className="mt-2 text-sm" style={{ color: "var(--text-secondary)" }}>
            Log in to save stocks to your watchlist, view past predictions, and manage alert configurations.
          </p>
          <div className="mt-6 flex flex-col gap-3">
            <Link
              href="/login"
              className="w-full rounded-md py-2.5 text-sm font-semibold transition-opacity hover:opacity-90"
              style={{
                backgroundColor: "var(--signal-up)",
                color: "var(--bg-base)",
              }}
            >
              Log In
            </Link>
            <Link
              href="/signup"
              className="w-full rounded-md border py-2.5 text-sm font-semibold transition-colors hover:bg-opacity-5"
              style={{
                borderColor: "var(--border-subtle)",
                color: "var(--text-primary)",
              }}
            >
              Create Account
            </Link>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-4xl px-6 py-8">
      {/* Profile Overview */}
      <div
        className="rounded-xl border p-6 shadow-md"
        style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border-subtle)" }}
      >
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <h1 className="text-2xl font-bold">User Profile</h1>
            <p className="mt-1 text-sm font-mono-data" style={{ color: "var(--text-secondary)" }}>
              {user.email}
            </p>
          </div>
          <button
            onClick={handleLogout}
            className="self-start rounded-md border px-4 py-2 text-sm font-semibold transition-colors hover:bg-opacity-10"
            style={{
              borderColor: "var(--signal-down)",
              color: "var(--signal-down)",
            }}
          >
            Log Out
          </button>
        </div>
        {error && (
          <div className="mt-4 rounded-md border p-3 text-sm" style={{ borderColor: "var(--signal-down)", color: "var(--signal-down)" }}>
            {error}
          </div>
        )}
      </div>

      {/* Watchlist Section */}
      <div className="mt-8">
        <div className="flex items-center justify-between border-b pb-3" style={{ borderColor: "var(--border-subtle)" }}>
          <h2 className="text-lg font-semibold">Your Watchlist</h2>
          <span className="rounded bg-opacity-10 px-2 py-0.5 text-xs font-semibold" style={{ backgroundColor: "var(--accent)", color: "var(--accent)" }}>
            {watchlist.length} Stocks
          </span>
        </div>

        {/* Add Ticker Form */}
        <form onSubmit={handleAdd} className="mt-4 flex max-w-md gap-3">
          <input
            type="text"
            required
            value={newTicker}
            onChange={(e) => setNewTicker(e.target.value)}
            placeholder="Search/Add symbol (e.g. AAPL)"
            className="flex-1 rounded-md border px-3 py-2 text-sm font-mono-data uppercase outline-none"
            style={{
              backgroundColor: "var(--bg-elevated)",
              borderColor: "var(--border-subtle)",
              color: "var(--text-primary)",
            }}
          />
          <button
            type="submit"
            disabled={actionLoading}
            className="rounded-md px-5 py-2 text-sm font-semibold transition-opacity hover:opacity-90 disabled:opacity-50"
            style={{
              backgroundColor: "var(--signal-up)",
              color: "var(--bg-base)",
            }}
          >
            {actionLoading ? "Adding..." : "Add"}
          </button>
        </form>

        {actionError && (
          <div className="mt-2 text-sm" style={{ color: "var(--signal-down)" }}>
            {actionError}
          </div>
        )}

        {/* Watchlist Table */}
        <div className="mt-6 overflow-hidden rounded-xl border" style={{ borderColor: "var(--border-subtle)" }}>
          {watchlist.length === 0 ? (
            <div className="p-8 text-center" style={{ backgroundColor: "var(--bg-surface)", color: "var(--text-secondary)" }}>
              No stocks in watchlist yet. Add one above to get started tracking.
            </div>
          ) : (
            <table className="w-full border-collapse text-left text-sm" style={{ backgroundColor: "var(--bg-surface)" }}>
              <thead>
                <tr className="border-b" style={{ borderColor: "var(--border-subtle)", backgroundColor: "var(--bg-elevated)" }}>
                  <th className="px-6 py-3 font-semibold">Ticker</th>
                  <th className="px-6 py-3 font-semibold">Added On</th>
                  <th className="px-6 py-3 font-semibold text-right">Actions</th>
                </tr>
              </thead>
             <tbody className="divide-y" style={{ borderColor: "var(--border-subtle)" }}>
                {watchlist.map((item) => (
                  <tr key={item.id} className="hover:bg-opacity-5 transition-colors">
                    <td className="px-6 py-4 font-mono-data font-semibold text-lg" style={{ color: "var(--text-primary)" }}>
                      {item.ticker}
                    </td>
                    <td className="px-6 py-4" style={{ color: "var(--text-secondary)" }}>
                      {new Date(item.added_at).toLocaleDateString(undefined, {
                        year: "numeric",
                        month: "short",
                        day: "numeric",
                      })}
                    </td>
                    <td className="px-6 py-4 text-right space-x-3">
                      <Link
                        href={`/dashboard?ticker=${item.ticker}`}
                        className="rounded px-3 py-1.5 text-xs font-semibold border transition-colors"
                        style={{
                          borderColor: "var(--border-subtle)",
                          backgroundColor: "var(--bg-elevated)",
                          color: "var(--text-primary)",
                        }}
                      >
                        Dashboard
                      </Link>
                      <button
                        onClick={() => handleRemove(item.ticker)}
                        disabled={actionLoading}
                        className="rounded px-3 py-1.5 text-xs font-semibold transition-colors hover:bg-opacity-10"
                        style={{
                          border: "1px solid var(--signal-down)",
                          color: "var(--signal-down)",
                        }}
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </main>
  );
}
