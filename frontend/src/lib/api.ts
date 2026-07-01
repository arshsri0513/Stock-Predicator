/**
 * Centralized API client.
 *
 * Why this file exists: every component that needs backend data should call
 * functions from here, rather than calling `fetch()` directly. This means
 * when we add JWT auth headers (Phase 12) or change the backend URL for
 * production, we change it in ONE place instead of hunting through every
 * component.
 */

import type {
  StockHistoryResponse,
  TechnicalIndicatorsResponse,
  StockInfo,
  ClassicalModelType,
  TrainResponse,
  PredictResponse,
  EvaluateResponse,
  NewsResponse,
  ApiErrorBody,
  UserResponse,
  TokenResponse,
  WatchlistItem,
} from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Custom error class so calling code can distinguish "the backend told us
 * something specific went wrong" (e.g. invalid ticker) from a generic
 * network failure. The `detail` field carries our backend's actual error
 * message (see app/main.py's error shape from Phase 8) so the UI can show
 * the REAL reason, not just a generic "something went wrong."
 */
export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}

/**
 * Get dynamic auth header from localStorage if running client-side.
 */
function getAuthHeaders(): Record<string, string> {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) {
      return { Authorization: `Bearer ${token}` };
    }
  }
  return {};
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    const body: ApiErrorBody = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail || res.statusText);
  }
  return res.json();
}

export async function apiPost<T>(path: string, data: unknown): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body: ApiErrorBody = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail || res.statusText);
  }
  return res.json();
}

export async function apiDelete<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "DELETE",
    headers: {
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    const body: ApiErrorBody = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail || res.statusText);
  }
  return res.status === 204 ? (null as T) : res.json().catch(() => null);
}

// Placeholder used since Phase 2 — proves the frontend can reach the
// backend's /health endpoint.
export async function checkBackendHealth() {
  return apiGet<{ status: string; environment: string }>("/health");
}

// ---- Stocks ----

export async function getStockHistory(
  ticker: string,
  period: string = "1y",
  interval: string = "1d"
): Promise<StockHistoryResponse> {
  return apiGet(`/stocks/${ticker}/history?period=${period}&interval=${interval}`);
}

export async function getTechnicalIndicators(
  ticker: string,
  period: string = "1y"
): Promise<TechnicalIndicatorsResponse> {
  return apiGet(`/stocks/${ticker}/technical-indicators?period=${period}`);
}

export async function getStockInfo(ticker: string): Promise<StockInfo> {
  return apiGet(`/stocks/${ticker}/info`);
}

// ---- Models ----

export async function trainModel(
  ticker: string,
  modelType: ClassicalModelType,
  period: string = "5y",
  horizon: number = 1
): Promise<TrainResponse> {
  return apiPost(`/models/train`, { ticker, model_type: modelType, period, horizon });
}

export async function getPrediction(
  ticker: string,
  modelType: string = "random_forest"
): Promise<PredictResponse> {
  return apiGet(`/models/${ticker}/predict?model_type=${modelType}`);
}

export async function evaluateModel(
  ticker: string,
  modelType: string = "random_forest",
  period: string = "2y"
): Promise<EvaluateResponse> {
  return apiGet(`/models/${ticker}/evaluate?model_type=${modelType}&period=${period}`);
}

// ---- News ----

export async function getNews(ticker: string, limit: number = 10): Promise<NewsResponse> {
  return apiGet(`/news/${ticker}?limit=${limit}`);
}


// ---- Auth & Profile (Phase 12) ----

export async function signup(email: string, password: string): Promise<UserResponse> {
  return apiPost<UserResponse>("/auth/signup", { email, password });
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  return apiPost<TokenResponse>("/auth/login", { email, password });
}

export async function getMe(): Promise<UserResponse> {
  return apiGet<UserResponse>("/auth/me");
}


// ---- Watchlist (Phase 12) ----

export async function getWatchlist(): Promise<WatchlistItem[]> {
  return apiGet<WatchlistItem[]>("/watchlist");
}

export async function addToWatchlist(ticker: string): Promise<WatchlistItem> {
  return apiPost<WatchlistItem>("/watchlist", { ticker });
}

export async function removeFromWatchlist(ticker: string): Promise<void> {
  return apiDelete<void>(`/watchlist/${ticker}`);
}

