"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { signup, ApiError } from "@/lib/api";

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError("Please fill in all fields.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await signup(email.trim(), password);
      setSuccess(true);
      setTimeout(() => {
        router.push("/login");
      }, 2000);
    } catch (e) {
      setError(e instanceof ApiError ? e.detail : "Sign up failed. Please try again.");
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
            <span style={{ color: "var(--signal-up)" }}>$</span> SIGNUP
          </h1>
          <p className="mt-2 text-sm" style={{ color: "var(--text-secondary)" }}>
            Create an account to save your watchlist and track stock predictions.
          </p>
        </div>

        {success ? (
          <div
            className="mt-6 rounded-md border p-4 text-center text-sm font-medium"
            style={{
              borderColor: "var(--signal-up)",
              color: "var(--signal-up)",
              backgroundColor: "rgba(45, 212, 168, 0.05)",
            }}
          >
            Account created successfully! Redirecting to login...
          </div>
        ) : (
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
                className="w-full rounded-md border px-3 py-2 text-sm outline-none transition-colors focus:border-opacity-100"
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

            <div>
              <label
                className="mb-1 block text-xs font-medium uppercase tracking-wide"
                style={{ color: "var(--text-secondary)" }}
              >
                Confirm Password
              </label>
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
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
              {loading ? "Creating Account..." : "Sign Up"}
            </button>
          </form>
        )}

        <div className="mt-6 text-center text-xs" style={{ color: "var(--text-secondary)" }}>
          Already have an account?{" "}
          <Link href="/login" className="underline hover:text-white" style={{ color: "var(--accent)" }}>
            Log In
          </Link>
        </div>
      </div>
    </main>
  );
}
