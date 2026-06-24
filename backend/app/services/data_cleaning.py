"""
Data cleaning utilities for raw OHLCV stock data.

Why this matters: yfinance data, while generally reliable, can have:
- Missing rows (market holidays are usually already excluded, but data
  provider hiccups can still leave gaps)
- NaN (Not a Number) values in specific cells if a data point failed to load
- Zero or negative prices in rare bad-data cases (a real bug we've seen
  happen with some tickers around corporate actions like delistings)

Feeding any of these directly into technical indicators or ML models
produces silently wrong results — NaN propagates through calculations,
and a model trained on a single bad zero-price row can learn nonsense.
We clean BEFORE any feature engineering happens.
"""

import pandas as pd


def clean_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean a raw OHLCV DataFrame in place-safe manner (returns a new copy).

    Cleaning steps, in order:
    1. Drop exact duplicate rows (can happen if the same date is fetched twice)
    2. Forward-fill missing values (use the last known good value)
    3. Drop any remaining rows that still have NaNs (e.g. if missing values
       are at the very start, where there's nothing earlier to forward-fill from)
    4. Remove rows with non-positive prices (data errors, not real trading days)
    5. Sort by date ascending (yfinance usually returns this already sorted,
       but we enforce it so downstream code can always rely on chronological order)

    Why forward-fill specifically (not interpolation or dropping)?
    Stock prices are not smoothly interpolatable — a missing Tuesday's price
    isn't the average of Monday and Wednesday, it's unknown. Forward-filling
    (carrying yesterday's close forward) is the standard, conservative
    convention in financial data processing: it says "assume nothing changed"
    rather than inventing a value that didn't exist.
    """
    cleaned = df.copy()

    # Step 1: remove duplicate dates
    cleaned = cleaned[~cleaned.index.duplicated(keep="first")]

    # Step 2: forward-fill missing values
    cleaned = cleaned.ffill()

    # Step 3: drop any rows still containing NaN (only possible at the very
    # start of the series, before any "last known value" exists)
    cleaned = cleaned.dropna()

    # Step 4: remove invalid (non-positive) price rows
    price_cols = [c for c in ["Open", "High", "Low", "Close"] if c in cleaned.columns]
    for col in price_cols:
        cleaned = cleaned[cleaned[col] > 0]

    # Step 5: ensure chronological order
    cleaned = cleaned.sort_index()

    return cleaned


def validate_ohlcv(df: pd.DataFrame) -> list[str]:
    """
    Run sanity checks on cleaned data and return a list of warning messages
    (empty list = no issues found). This doesn't raise errors — it surfaces
    concerns so calling code (or a human) can decide what to do.

    Checks performed:
    - High should never be lower than Low
    - Close should fall within [Low, High] for that day
    - No unreasonably large single-day jumps (possible data error, or a
      genuine stock split that wasn't adjusted — worth flagging either way)
    """
    warnings = []

    if (df["High"] < df["Low"]).any():
        warnings.append("Found rows where High < Low — likely a data error.")

    if ((df["Close"] > df["High"]) | (df["Close"] < df["Low"])).any():
        warnings.append("Found rows where Close is outside the [Low, High] range.")

    daily_pct_change = df["Close"].pct_change().abs()
    if (daily_pct_change > 0.5).any():
        warnings.append(
            "Found single-day price moves greater than 50% — verify this isn't "
            "a data error or an unadjusted stock split."
        )

    return warnings
