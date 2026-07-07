"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

/**
 * Top navigation bar, present on every page via the root layout.
 *
 * Design intent: dense, ticker-strip feel rather than a soft marketing
 * navbar -- monospace wordmark, hairline border instead of a shadow,
 * active link marked with the signal-up color rather than a background pill.
 */

import { useEffect, useState } from "react";

const NAV_LINKS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/markets", label: "Markets" },
  { href: "/predict", label: "Predictions" },
  { href: "/watchlist", label: "Watchlist" },
  { href: "/portfolio", label: "Portfolio" },
  { href: "/alerts", label: "Alerts" },
  { href: "/settings", label: "Settings" }, // 👈 Add this line
  { href: "/news", label: "News" },
];

export default function Navbar() {
  const pathname = usePathname();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    function checkAuth() {
     setIsLoggedIn(!!localStorage.getItem("access_token"));
    }

    checkAuth();
    window.addEventListener("auth-change", checkAuth);
    return () => window.removeEventListener("auth-change", checkAuth);
  }, []);

  function handleLogout() {
    localStorage.removeItem("access_token");
    setIsLoggedIn(false);
    window.dispatchEvent(new Event("auth-change"));
  }

  return (
    <nav
      className="sticky top-0 z-50 border-b"
      style={{ borderColor: "var(--border-subtle)", backgroundColor: "var(--bg-surface)" }}
    >
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-6">
        <Link
  href="/dashboard"
  className="flex items-center gap-3 transition hover:opacity-90"
>
  <div
    className="flex h-10 w-10 items-center justify-center rounded-xl text-lg font-bold"
    style={{
      backgroundColor: "rgba(45,212,168,0.12)",
      color: "var(--signal-up)",
    }}
  >
    📈
  </div>

  <div>
    <h1 className="text-lg font-bold">
      StockPredict AI
    </h1>

    <p
      className="text-xs"
      style={{
        color: "var(--text-secondary)",
      }}
    >
      Predict Smarter.
    </p>
  </div>
</Link>

       {/* Center Navigation */}
<div className="flex items-center gap-2">

  {NAV_LINKS.map((link) => {
    const isActive = pathname === link.href;

    return (
      <Link
        key={link.href}
        href={link.href}
        className="rounded px-3 py-2 text-sm font-medium transition-colors"
        style={{
          color: isActive
            ? "var(--signal-up)"
            : "var(--text-secondary)",
        }}
      >
        {link.label}
      </Link>
    );
  })}

</div>

{/* Right Side */}
<div className="flex items-center gap-4">

  {isLoggedIn ? (
    <>
      <Link
        href="/profile"
        className="rounded px-3 py-2 text-sm font-medium transition-colors"
        style={{
          color:
            pathname === "/profile"
              ? "var(--signal-up)"
              : "var(--text-secondary)",
        }}
      >
        Profile
      </Link>

      <button
        onClick={handleLogout}
        className="rounded px-3 py-2 text-sm font-medium transition-colors"
        style={{
          color: "var(--signal-down)",
        }}
      >
        Logout
      </button>
    </>
  ) : (
    <Link
      href="/login"
      className="rounded px-3 py-2 text-sm font-medium transition-colors"
      style={{
        color:
          pathname === "/login"
            ? "var(--signal-up)"
            : "var(--text-secondary)",
      }}
    >
      Login
    </Link>
  )}

</div>
      </div>
    </nav>
  );
}
