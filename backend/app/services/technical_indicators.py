"""
Technical indicator calculations.

This module adds indicator columns to a cleaned OHLCV DataFrame (the output
of app.services.data_cleaning.clean_ohlcv). We use the `ta` library for the
actual math rather than hand-rolling formulas — financial indicator
calculations have subtle edge cases (rolling window boundaries, smoothing
seed values) that are easy to get subtly wrong, and `ta` is widely used and
well-tested.

Indicators added here become FEATURES for the ML models in Phase 5, and are
also returned directly to the frontend for charting in Phase 11.
"""

import pandas as pd
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator


def add_moving_averages(df: pd.DataFrame, windows: list[int] = [20, 50]) -> pd.DataFrame:
    """
    Add SMA and EMA columns for each window size in `windows`.

    Why offer multiple windows? A 20-day average reacts to short-term trend
    shifts; a 50-day average reflects the longer-term trend. Comparing them
    (e.g. "is the 20-day above the 50-day?") is itself a common trading
    signal called a "moving average crossover."
    """
    out = df.copy()
    for window in windows:
        out[f"sma_{window}"] = SMAIndicator(close=out["Close"], window=window).sma_indicator()
        out[f"ema_{window}"] = EMAIndicator(close=out["Close"], window=window).ema_indicator()
    return out


def add_rsi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """
    Add RSI (Relative Strength Index), default 14-day window — the
    conventional standard period used across virtually all trading platforms.
    """
    out = df.copy()
    out["rsi_14"] = RSIIndicator(close=out["Close"], window=window).rsi()
    return out


def add_macd(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add MACD line, signal line, and histogram using the conventional
    12/26/9 periods (fast EMA / slow EMA / signal EMA) — the industry-standard
    default since MACD's invention in the 1970s.
    """
    out = df.copy()
    macd = MACD(close=out["Close"], window_fast=12, window_slow=26, window_sign=9)
    out["macd_line"] = macd.macd()
    out["macd_signal"] = macd.macd_signal()
    out["macd_histogram"] = macd.macd_diff()
    return out


def add_bollinger_bands(df: pd.DataFrame, window: int = 20, std_dev: int = 2) -> pd.DataFrame:
    """
    Add Bollinger Bands: middle (SMA), upper, and lower bands.
    Default window=20, std_dev=2 are the original, most widely used settings
    (as defined by John Bollinger himself).
    """
    out = df.copy()
    bb = BollingerBands(close=out["Close"], window=window, window_dev=std_dev)
    out["bb_middle"] = bb.bollinger_mavg()
    out["bb_upper"] = bb.bollinger_hband()
    out["bb_lower"] = bb.bollinger_lband()
    return out


def add_atr(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """
    Add ATR (Average True Range) — a pure volatility measure, default 14-day
    window (the period Welles Wilder originally proposed when he invented ATR).

    Note: the `ta` library's AverageTrueRange defaults early "warm-up" rows
    (before `window` days of history exist) to 0 rather than NaN. A 0 here
    is misleading — it reads as "zero volatility that day" when the real
    meaning is "not enough data yet to calculate this." We explicitly
    overwrite the first `window` rows with NaN so ATR behaves consistently
    with every other indicator in this module (and so Phase 5's
    .dropna()-based cleanup correctly excludes these rows from training).
    """
    out = df.copy()
    out["atr_14"] = AverageTrueRange(
        high=out["High"], low=out["Low"], close=out["Close"], window=window
    ).average_true_range()
    out.iloc[:window, out.columns.get_loc("atr_14")] = float("nan")
    return out


def add_volume_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add OBV (On-Balance Volume) — tracks cumulative volume flow direction.
    """
    out = df.copy()
    out["obv"] = OnBalanceVolumeIndicator(
        close=out["Close"], volume=out["Volume"]
    ).on_balance_volume()
    return out


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience function: applies every indicator in this module in sequence.
    This is what the API route and the ML feature pipeline will call.
    """
    out = df.copy()
    out = add_moving_averages(out)
    out = add_rsi(out)
    out = add_macd(out)
    out = add_bollinger_bands(out)
    out = add_atr(out)
    out = add_volume_indicators(out)
    return out
