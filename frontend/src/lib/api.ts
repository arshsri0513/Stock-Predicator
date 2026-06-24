/**
 * Centralized API client.
 *
 * Why this file exists: every component that needs backend data should call
 * functions from here, rather than calling `fetch()` directly. This means
 * when we add JWT auth headers (Phase 12) or change the backend URL for
 * production, we change it in ONE place instead of hunting through every
 * component.
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`);
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// Placeholder used by the skeleton — proves the frontend can reach the
// backend's /health endpoint. Real domain-specific calls (getStockHistory,
// getPrediction, etc.) get added in Phase 8 once those endpoints exist.
export async function checkBackendHealth() {
  return apiGet<{ status: string; environment: string }>("/health");
}
