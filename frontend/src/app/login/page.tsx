"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { login, ApiError } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError("Please enter your email and password.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await login(email.trim(), password);
      // Store token in local storage
      localStorage.setItem("token", res.access_token);
      // Redirect to profile page
      router.push("/profile");
      // Trigger a window reload/event to update state globally
      setTimeout(() => {
        window.dispatchEvent(new Event("auth-change"));
      }, 100);
    } catch (e) {
      setError(e instanceof ApiError ? e.detail : "Login failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-[calc(100vh-3.5rem)] max-w-md flex-col justify-center px-6 py-12">
      <div
        className="rounded-xl border p-8 shadow-xl"
        style={{
          backgroundColor: "var(--bg-surface)",
          borderColor: "var(--border-subtle)",
        }}
      >
        <div className="text-center">
          <h1 className="font-mono-data text-2xl font-bold tracking-tight">
            <span style={{ color: "var(--signal-up)" }}>$</span> LOGIN
          </h1>
          <p className="mt-2 text-sm" style={{ color: "var(--text-secondary)" }}>
            Welcome back! Enter your details to log into your account.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          {error && (
            <div
              className="rounded-md border p-3 text-sm"
              style={{
                borderColor: "var(--signal-down)",
                color: "var(--signal-down)",
                backgroundColor: "rgba(224, 101, 79, 0.05)",
              }}
            >
              {error}
            </div>
          )}

          <div>
            <label
              className="mb-1 block text-xs font-medium uppercase tracking-wide"
              style={{ color: "var(--text-secondary)" }}
            >
              Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full rounded-md border px-3 py-2 text-sm outline-none transition-colors"
              style={{
                backgroundColor: "var(--bg-elevated)",
                borderColor: "var(--border-subtle)",
                color: "var(--text-primary)",
              }}
            />
          </div>

          <div>
            <label
              className="mb-1 block text-xs font-medium uppercase tracking-wide"
              style={{ color: "var(--text-secondary)" }}
            >
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full rounded-md border px-3 py-2 text-sm outline-none"
              style={{
                backgroundColor: "var(--bg-elevated)",
                borderColor: "var(--border-subtle)",
                color: "var(--text-primary)",
              }}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md py-2 text-sm font-semibold transition-opacity hover:opacity-90 disabled:opacity-50"
            style={{
              backgroundColor: "var(--signal-up)",
              color: "var(--bg-base)",
            }}
          >
            {loading ? "Logging In..." : "Log In"}
          </button>
        </form>

        <div className="mt-6 text-center text-xs" style={{ color: "var(--text-secondary)" }}>
          Don&apos;t have an account?{" "}
          <Link href="/signup" className="underline hover:text-white" style={{ color: "var(--accent)" }}>
            Sign Up
          </Link>
        </div>
      </div>
    </main>
  );
}
