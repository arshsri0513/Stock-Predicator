import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Stock Predictor",
  description: "AI-powered stock market prediction and analytics",
};

// This layout wraps EVERY page in the app (App Router convention).
// Anything shared across all pages — like a navbar — will eventually
// be added here in Phase 10, once we build the Navbar component.
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
