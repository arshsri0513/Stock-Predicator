"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";

/**
 * Ticker search bar -- the primary entry point into the app from Home.
 * On submit, navigates to /dashboard?ticker=XXX rather than calling the
 * API directly itself; the Dashboard page owns fetching, this component
 * only owns capturing intent (what ticker does the person want to see).
 */
export default function SearchBar() {
  const [value, setValue] = useState("");
  const router = useRouter();

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const ticker = value.trim().toUpperCase();
    if (!ticker) return;
    router.push(`/dashboard?ticker=${ticker}`);
  }

  return (
    <form onSubmit={handleSubmit} className="flex w-full max-w-md gap-2">
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="AAPL, TSLA, MSFT..."
        className="font-mono-data flex-1 rounded-md border px-4 py-2.5 text-sm outline-none transition-colors focus:ring-1"
        style={{
          backgroundColor: "var(--bg-elevated)",
          borderColor: "var(--border-subtle)",
          color: "var(--text-primary)",
        }}
        aria-label="Stock ticker symbol"
      />
      <button
        type="submit"
        className="rounded-md px-5 py-2.5 text-sm font-semibold transition-opacity hover:opacity-90"
        style={{ backgroundColor: "var(--signal-up)", color: "var(--bg-base)" }}
      >
        Search
      </button>
    </form>
  );
}
