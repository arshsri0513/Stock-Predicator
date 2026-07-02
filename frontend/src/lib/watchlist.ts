import { apiGet, apiPost } from "./api";

export interface WatchlistItem {
  id: string;
  ticker: string;
  added_at: string;
}

export async function getWatchlist(): Promise<WatchlistItem[]> {
  return apiGet("/watchlist");
}

export async function addToWatchlist(
  ticker: string
): Promise<WatchlistItem> {
  return apiPost("/watchlist", {
    ticker,
  });
}

export async function removeFromWatchlist(
  ticker: string
): Promise<void> {
  const token = localStorage.getItem("access_token");

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/watchlist/${ticker}`,
    {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error("Unable to remove stock.");
  }
}