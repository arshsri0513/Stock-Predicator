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

const NAV_LINKS = [
  { href: "/", label: "Home" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/predict", label: "Prediction" },
  { href: "/charts", label: "Charts" },
  { href: "/news", label: "News" },
  { href: "/profile", label: "Profile" },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav
      className="sticky top-0 z-50 border-b"
      style={{ borderColor: "var(--border-subtle)", backgroundColor: "var(--bg-surface)" }}
    >
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-6">
        <Link href="/" className="font-mono-data text-lg font-semibold tracking-tight">
          <span style={{ color: "var(--signal-up)" }}>$</span> STOCKPREDICT
        </Link>

        <div className="flex items-center gap-1">
          {NAV_LINKS.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className="rounded px-3 py-1.5 text-sm font-medium transition-colors"
                style={{
                  color: isActive ? "var(--signal-up)" : "var(--text-secondary)",
                }}
              >
                {link.label}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
