/**
 * TypeScript types mirroring the backend's Pydantic schemas exactly.
 *
 * Why duplicate these instead of generating them automatically? FastAPI
 * CAN auto-generate an OpenAPI spec we could codegen types from, but for a
 * project this size, hand-maintained types that we deliberately keep in
 * sync are simpler to understand and debug as a beginner than introducing
 * a codegen build step. If the API surface grows much larger later, that
 * tradeoff might flip -- worth knowing as a real engineering decision, not
 * an oversight.
 */

// ---- Stocks (Phase 3-4) ----

export interface OHLCVRow {
  Date: string;
  Open: number;
  High: number;
  Low: number;
  Close: number;
  Volume: number;
  Dividends: number;
  "Stock Splits": number;
}

export interface StockHistoryResponse {
  ticker: string;
  period: string;
  interval: string;
  rows: number;
  warnings: string[];
  data: OHLCVRow[];
}

export interface IndicatorRow extends OHLCVRow {
  sma_20: number | null;
  ema_20: number | null;
  sma_50: number | null;
  ema_50: number | null;
  rsi_14: number | null;
  macd_line: number | null;
  macd_signal: number | null;
  macd_histogram: number | null;
  bb_middle: number | null;
  bb_upper: number | null;
  bb_lower: number | null;
  atr_14: number | null;
  obv: number | null;
}

export interface TechnicalIndicatorsResponse {
  ticker: string;
  period: string;
  rows: number;
  data: IndicatorRow[];
}

export interface StockInfo {
  symbol: string;
  name: string;
  sector: string;
  industry: string;
  market_cap: number;
  currency: string;
}

// ---- Models (Phase 5-6, 8) ----

export type ClassicalModelType = "linear_regression" | "random_forest" | "xgboost";
export type DLModelType = "lstm" | "gru" | "transformer";

export interface ModelMetrics {
  rmse: number;
  mae: number;
  mape: number;
  r2_score: number;
}

export interface TrainResponse {
  ticker: string;
  model_type: string;
  rows_trained_on: number;
  metrics: ModelMetrics;
  model_path: string;
}

export interface PredictResponse {
  ticker: string;
  model_type: string;
  predicted_close: number;
  based_on_date: string;
}

export interface EvaluateResponse {
  ticker: string;
  model_type: string;
  rows_evaluated_on: number;
  metrics: ModelMetrics;
  evaluated_on_period: string;
}

// ---- News (Phase 7) ----

export interface NewsItem {
  title: string;
  publisher: string;
  link: string;
  published: string;
  vader_compound: number;
  vader_label: "positive" | "neutral" | "negative";
  finbert_label: string;
  finbert_confidence: number;
}

export interface NewsResponse {
  ticker: string;
  article_count: number;
  articles: NewsItem[];
  average_vader_compound: number;
}

// ---- Errors ----

export interface ApiErrorBody {
  detail: string;
}


// ---- Auth & Watchlist (Phase 12) ----

export interface UserResponse {
  id: string;
  email: string;
}

export interface TokenResponse {
  access_token: string;
}

export interface WatchlistItem {
  id: string;
  ticker: string;
  added_at: string;
}
