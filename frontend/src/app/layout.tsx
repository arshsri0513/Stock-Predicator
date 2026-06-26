import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "Stock Predictor",
  description: "AI-powered stock market prediction and analytics",
};

// This layout wraps EVERY page in the app (App Router convention).
// Navbar lives here so it's present on every page without each page
// needing to import and render it individually.
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        {children}
      </body>
    </html>
  );
}
