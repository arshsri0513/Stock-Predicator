"use client";

import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export default function ThemeSwitcher() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <select
      value={theme}
      onChange={(e) => setTheme(e.target.value)}
      className="rounded-lg border px-3 py-2 text-sm"
      style={{
        backgroundColor: "var(--bg-surface)",
        color: "var(--text-primary)",
        borderColor: "var(--border-subtle)",
      }}
    >
      <option value="light">☀️ Light</option>
      <option value="dark">🌙 Dark</option>
      <option value="system">💻 System</option>
    </select>
  );
}