import pandas as pd
import numpy as np
from typing import Dict, Optional, Any
from sklearn.linear_model import LinearRegression


def _compute_trend_indicator(
    df, value_column, window=20, min_periods=None, use_abs_mean=False
):
    """
    Generic function to compute trend indicators using linear regression.
    """
    result_df = df.copy()
    result_df = result_df.sort_values("timestamp").reset_index(drop=True)

    if min_periods is None:
        min_periods = window

    def calc_trend(window_series):
        if len(window_series) < min_periods:
            return np.nan

        y = window_series.values
        x = np.arange(len(y)).reshape(-1, 1)

        model = LinearRegression().fit(x, y)
        slope = model.coef_[0]

        if use_abs_mean:
            divisor = np.mean(np.abs(y))
        else:
            divisor = np.mean(y)

        return slope / divisor if divisor != 0 else 0

    trend_column = f"{value_column}_trend"
    result_df[trend_column] = (
        result_df[value_column]
        .rolling(window=window, min_periods=min_periods)
        .apply(calc_trend, raw=False)
    )

    return result_df


def compute_funding_trend(funding_df, window=20, min_periods=None):
    """
    Computes the funding rate trend indicator as the normalized slope of
    a linear regression over a rolling window.
    """
    return _compute_trend_indicator(
        funding_df, "funding_rate", window, min_periods, use_abs_mean=True
    )


def compute_oi_price_divergence(oi_df, price_df):
    """
    Computes divergence between open interest and price.

    The divergence is defined as the difference between the percentage change
    of open interest and the percentage change of the closing price.

    Parameters:
      oi_df (pd.DataFrame): DataFrame with ['timestamp', 'open_interest'].
      price_df (pd.DataFrame): DataFrame with ['timestamp', 'close'].

    Returns:
      pd.DataFrame: Merged DataFrame with new columns for percentage changes and divergence.
    """
    # Use merge_asof to join on the nearest timestamps
    df = pd.merge_asof(
        oi_df[["timestamp", "open_interest"]].sort_values("timestamp"),
        price_df[["timestamp", "close"]].sort_values("timestamp"),
        on="timestamp",
        direction="nearest",
    )
    df["oi_pct_change"] = df["open_interest"].pct_change()
    df["price_pct_change"] = df["close"].pct_change()
    df["oi_price_divergence"] = df["oi_pct_change"] - df["price_pct_change"]
    return df


def compute_oi_volume_ratio(oi_df, price_df):
    """
    Computes the ratio of open interest to trading volume.

    This indicator can help assess the relative commitment of market participants.

    Parameters:
      oi_df (pd.DataFrame): DataFrame with ['timestamp', 'open_interest'].
      price_df (pd.DataFrame): DataFrame with ['timestamp', 'volume'].

    Returns:
      pd.DataFrame: Merged DataFrame with a new column 'oi_volume_ratio'.
    """
    df = pd.merge_asof(
        oi_df.sort_values("timestamp"),
        price_df.sort_values("timestamp"),
        on="timestamp",
        direction="nearest",
    )
    df["oi_volume_ratio"] = df["open_interest"] / df["volume"].replace(0, np.nan)
    return df


# 6. Squeeze Detection Indicator
def detect_squeezes(
    liquidation_df, funding_df, threshold_multiplier=2, window=20, min_periods=5
):
    """
    Detects potential short and long squeeze events with improved efficiency.
    """
    if not all(col in liquidation_df.columns for col in ["timestamp", "long", "short"]):
        raise ValueError(
            "Liquidation data must have 'timestamp', 'long', and 'short' columns"
        )

    # Fixed: Remove the tolerance parameter which can cause issues with millisecond timestamps
    df = pd.merge_asof(
        funding_df[["timestamp", "funding_rate"]].sort_values("timestamp"),
        liquidation_df[["timestamp", "long", "short"]].sort_values("timestamp"),
        on="timestamp",
        direction="nearest",
    )

    # Use vectorized operations for all statistics
    for col in ["long", "short"]:
        # Calculate rolling statistics
        df[f"{col}_liq_mean"] = (
            df[col].rolling(window=window, min_periods=min_periods).mean()
        )
        df[f"{col}_liq_std"] = (
            df[col].rolling(window=window, min_periods=min_periods).std()
        )
        # Calculate z-scores with better NaN handling
        df[f"{col}_liq_z"] = np.where(
            df[f"{col}_liq_std"] > 0,
            (df[col] - df[f"{col}_liq_mean"]) / df[f"{col}_liq_std"],
            np.nan,
        )

    # Funding rate statistics
    df["funding_mean"] = (
        df["funding_rate"].rolling(window=window, min_periods=min_periods).mean()
    )
    df["funding_std"] = (
        df["funding_rate"].rolling(window=window, min_periods=min_periods).std()
    )

    # Squeeze conditions with better handling of NaN values
    df["potential_short_squeeze"] = (
        (
            df["funding_rate"]
            > df["funding_mean"] + threshold_multiplier * df["funding_std"]
        )
        & (df["short_liq_z"] > threshold_multiplier)
        & (~df["short_liq_z"].isna())
    )

    df["potential_long_squeeze"] = (
        (
            df["funding_rate"]
            < df["funding_mean"] - threshold_multiplier * df["funding_std"]
        )
        & (df["long_liq_z"] > threshold_multiplier)
        & (~df["long_liq_z"].isna())
    )

    # Add squeeze strength indicators
    df["short_squeeze_strength"] = np.where(
        df["potential_short_squeeze"],
        df["short_liq_z"]
        * (df["funding_rate"] - df["funding_mean"])
        / df["funding_std"],
        np.nan,
    )

    df["long_squeeze_strength"] = np.where(
        df["potential_long_squeeze"],
        df["long_liq_z"]
        * (df["funding_mean"] - df["funding_rate"])
        / df["funding_std"],
        np.nan,
    )

    return df


def detect_ls_ratio_extremes(ls_ratio_df, window=50, z_threshold=2.0, min_periods=None):
    """
    Detects extreme values in the long/short ratio based on historical standard deviations.

    This can identify unusual market sentiment that might precede significant price moves.

    Parameters:
      ls_ratio_df (pd.DataFrame): DataFrame with ['timestamp', 'long_short_ratio']
      window (int): Lookback window for calculating statistics (default: 50)
      z_threshold (float): Z-score threshold for extreme values (default: 2.0)
      min_periods (int): Minimum observations required

    Returns:
      pd.DataFrame: DataFrame with added columns for z-scores and extreme value flags
    """
    if min_periods is None:
        min_periods = window // 2

    result_df = ls_ratio_df.copy().sort_values("timestamp").reset_index(drop=True)

    # Calculate rolling mean and standard deviation
    result_df["ls_ratio_mean"] = (
        result_df["long_short_ratio"]
        .rolling(window=window, min_periods=min_periods)
        .mean()
    )

    result_df["ls_ratio_std"] = (
        result_df["long_short_ratio"]
        .rolling(window=window, min_periods=min_periods)
        .std()
    )

    # Calculate z-scores
    result_df["ls_ratio_z_score"] = (
        result_df["long_short_ratio"] - result_df["ls_ratio_mean"]
    ) / result_df["ls_ratio_std"].replace(0, np.nan)

    # Flag extreme values
    result_df["extreme_bullish"] = result_df["ls_ratio_z_score"] > z_threshold
    result_df["extreme_bearish"] = result_df["ls_ratio_z_score"] < -z_threshold

    # Calculate days since last extreme value (useful for timing signals)
    result_df["days_since_extreme"] = (
        ~(result_df["extreme_bullish"] | result_df["extreme_bearish"])
    ).cumsum()

    # Reset counter when a new extreme is found
    result_df.loc[
        result_df["extreme_bullish"] | result_df["extreme_bearish"],
        "days_since_extreme",
    ] = 0

    return result_df


def calculate_derivative_indicators(
    data_dict: Dict[str, pd.DataFrame],
    price_data: Optional[pd.DataFrame] = None,
    window: int = 20,
) -> pd.DataFrame:
    """
    Calculates the 5 core indicators selected for trading:
    1. Squeeze Detection
    2. OI Price Divergence
    3. Long/Short Ratio Extremes
    4. Funding Rate Trend
    5. OI-to-Volume Ratio

    Parameters:
        data_dict: Dictionary with merged data from CoinalyzeDataProvider
        price_data: DataFrame with price and volume data (must have timestamp, close, volume)
        window: Window size for indicator calculations

    Returns:
        DataFrame with all calculated indicators
    """
    if "merged" not in data_dict:
        raise ValueError("Failed to retrieve consolidated data")

    df = data_dict["merged"].copy()

    # Ensure timestamps are properly handled
    if "timestamp" in df.columns:
        # Convert timestamps for plotting if they're in milliseconds
        if df["timestamp"].iloc[0] > 1e12:
            df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
        else:
            df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
    else:
        raise ValueError("Timestamp column missing in data")

    # Check if price data is available and prepare it
    if price_data is not None:
        # Ensure price_data has proper timestamp format
        if "timestamp" not in price_data.columns:
            raise ValueError("Price data must contain a timestamp column")

        # Convert timestamp to datetime if needed
        if "datetime" not in price_data.columns:
            if price_data["timestamp"].iloc[0] > 1e12:
                price_data["datetime"] = pd.to_datetime(
                    price_data["timestamp"], unit="ms"
                )
            else:
                price_data["datetime"] = pd.to_datetime(
                    price_data["timestamp"], unit="s"
                )

        # 1. Calculate OI Price Divergence (needs price data)
        if "open_interest" in df.columns and "close" in price_data.columns:
            try:
                oi_price_div = compute_oi_price_divergence(
                    df[["timestamp", "open_interest"]],
                    price_data[["timestamp", "close"]],
                )
                df = pd.merge_asof(
                    df.sort_values("timestamp"),
                    oi_price_div[
                        [
                            "timestamp",
                            "oi_pct_change",
                            "price_pct_change",
                            "oi_price_divergence",
                        ]
                    ],
                    on="timestamp",
                    direction="nearest",
                )
            except Exception as e:
                print(f"Warning: Failed to calculate OI Price Divergence: {e}")

        # 2. Calculate OI-to-Volume Ratio (needs volume data)
        if "open_interest" in df.columns and "volume" in price_data.columns:
            try:
                oi_vol_ratio = compute_oi_volume_ratio(
                    df[["timestamp", "open_interest"]],
                    price_data[["timestamp", "volume"]],
                )
                df = pd.merge_asof(
                    df.sort_values("timestamp"),
                    oi_vol_ratio[["timestamp", "oi_volume_ratio"]],
                    on="timestamp",
                    direction="nearest",
                )
            except Exception as e:
                print(f"Warning: Failed to calculate OI Volume Ratio: {e}")

    # 3. Calculate Funding Rate Trend (doesn't need price data)
    if "funding_rate" in df.columns:
        try:
            funding_trend = compute_funding_trend(
                df[["timestamp", "funding_rate"]], window=window
            )
            df = pd.merge_asof(
                df.sort_values("timestamp"),
                funding_trend[["timestamp", "funding_rate_trend"]],
                on="timestamp",
                direction="nearest",
            )
        except Exception as e:
            print(f"Warning: Failed to calculate Funding Rate Trend: {e}")

    # 4. Calculate Squeeze Detection (doesn't need price data)
    if "long" in df.columns and "short" in df.columns and "funding_rate" in df.columns:
        try:
            squeeze_df = detect_squeezes(
                df[["timestamp", "long", "short"]],
                df[["timestamp", "funding_rate"]],
                window=window,
            )

            for col in [
                "potential_short_squeeze",
                "potential_long_squeeze",
                "short_squeeze_strength",
                "long_squeeze_strength",
            ]:
                if col in squeeze_df.columns:
                    df[col] = squeeze_df[col]
        except Exception as e:
            print(f"Warning: Failed to detect squeezes: {e}")

    # 5. Calculate Long/Short Ratio Extremes (doesn't need price data)
    if "long_short_ratio" in df.columns:
        try:
            ls_extremes_df = detect_ls_ratio_extremes(
                df[["timestamp", "long_short_ratio"]],
                window=window * 2,
                z_threshold=2.0,
            )
            for col in [
                "ls_ratio_z_score",
                "extreme_bullish",
                "extreme_bearish",
                "days_since_extreme",
            ]:
                if col in ls_extremes_df.columns:
                    df[col] = ls_extremes_df[col]
        except Exception as e:
            print(f"Warning: Failed to detect L/S ratio extremes: {e}")

    return df


def generate_indicator_narrative(
    df: pd.DataFrame, lookback_periods: int = 12, timestamp=None
) -> Dict[str, Any]:
    """
    Generates a narrative description of the indicators considering recent history

    Parameters:
        df: DataFrame with calculated indicators
        lookback_periods: Number of recent periods to analyze (default 12 periods)
        timestamp: Optional specific timestamp to analyze (will use most recent if None)

    Returns:
        Dictionary with narrative descriptions and numerical values
    """
    # Input validation
    if df.empty:
        raise ValueError("DataFrame is empty")

    if "timestamp" not in df.columns:
        raise ValueError("DataFrame must contain a timestamp column")

    # Get the recent data window
    if timestamp is None:
        df = df.sort_values("timestamp", ascending=False)
        end_timestamp = df["timestamp"].iloc[0]
    else:
        end_timestamp = timestamp

    # Find the closest timestamp and get recent window
    idx = (df["timestamp"] - end_timestamp).abs().idxmin()
    recent_df = (
        df.iloc[max(0, idx - lookback_periods + 1) : idx + 1].copy()
        if idx > 0
        else df.head(min(lookback_periods, len(df)))
    )

    # Ensure we're working with sorted data
    recent_df = recent_df.sort_values("timestamp").reset_index(drop=True)

    # Get the latest row for current values
    latest_row = recent_df.iloc[-1]

    report = {
        "timestamp": end_timestamp,
        "datetime": latest_row.get(
            "datetime", pd.to_datetime(end_timestamp, unit="ms")
        ),
        "indicators": {},
        "signals": {},
        "summary": "",
        "trends": {},  # New section for trend analysis
    }

    # Initialize trend variables
    funding_trend = None
    div_trend = None
    ls_trend = None

    # 1. Funding Rate Analysis
    if "funding_rate" in recent_df.columns:
        current_funding = latest_row["funding_rate"]
        avg_funding = recent_df["funding_rate"].mean()
        funding_trend = recent_df["funding_rate"].diff().mean()  # Direction of change

        report["indicators"]["funding_rate"] = {
            "current": current_funding,
            "average": avg_funding,
            "trend": funding_trend,
            "description": f"Funding rate is {current_funding:.4f} ",
        }

        if abs(current_funding) > abs(avg_funding * 1.5):
            report["indicators"]["funding_rate"]["description"] += (
                f"(significantly {'higher' if current_funding > 0 else 'lower'} than {lookback_periods}-period average of {avg_funding:.4f}). "
            )

        if abs(funding_trend) > 0.0001:
            report["indicators"]["funding_rate"]["description"] += (
                f"Funding trend is {'increasing' if funding_trend > 0 else 'decreasing'}. "
            )

    # 2. Squeeze Analysis with Recent History
    if all(
        col in recent_df.columns
        for col in ["potential_short_squeeze", "potential_long_squeeze"]
    ):
        recent_short_squeezes = recent_df["potential_short_squeeze"].sum()
        recent_long_squeezes = recent_df["potential_long_squeeze"].sum()

        report["signals"]["squeeze_pressure"] = {
            "short_squeeze_signals": recent_short_squeezes,
            "long_squeeze_signals": recent_long_squeezes,
            "description": "",
        }

        if recent_short_squeezes > 0:
            report["signals"]["squeeze_pressure"]["description"] += (
                f"Detected {recent_short_squeezes} short squeeze signals in last {lookback_periods} periods. "
            )
            if latest_row.get("potential_short_squeeze", False):
                report["signals"]["squeeze_pressure"]["description"] += (
                    "Current period shows active short squeeze conditions. "
                )

            # Get strength if available
            if "short_squeeze_strength" in latest_row and not pd.isna(
                latest_row["short_squeeze_strength"]
            ):
                report["signals"]["squeeze_pressure"]["short_strength"] = latest_row[
                    "short_squeeze_strength"
                ]
                report["signals"]["squeeze_pressure"]["description"] += (
                    f"Short squeeze strength: {latest_row['short_squeeze_strength']:.2f}. "
                )

        if recent_long_squeezes > 0:
            report["signals"]["squeeze_pressure"]["description"] += (
                f"Detected {recent_long_squeezes} long squeeze signals in last {lookback_periods} periods. "
            )
            if latest_row.get("potential_long_squeeze", False):
                report["signals"]["squeeze_pressure"]["description"] += (
                    "Current period shows active long squeeze conditions. "
                )

            # Get strength if available
            if "long_squeeze_strength" in latest_row and not pd.isna(
                latest_row["long_squeeze_strength"]
            ):
                report["signals"]["squeeze_pressure"]["long_strength"] = latest_row[
                    "long_squeeze_strength"
                ]
                report["signals"]["squeeze_pressure"]["description"] += (
                    f"Long squeeze strength: {latest_row['long_squeeze_strength']:.2f}. "
                )

        if recent_short_squeezes == 0 and recent_long_squeezes == 0:
            report["signals"]["squeeze_pressure"]["description"] = (
                "No squeeze conditions detected in recent periods."
            )

    # 3. OI Price Divergence Trend
    if "oi_price_divergence" in recent_df.columns:
        current_div = latest_row["oi_price_divergence"]
        avg_div = recent_df["oi_price_divergence"].mean()
        div_trend = recent_df["oi_price_divergence"].diff().mean()

        report["indicators"]["oi_price_divergence"] = {
            "current": current_div,
            "average": avg_div,
            "trend": div_trend,
            "description": "",
        }

        # Analyze divergence pattern
        if abs(current_div) > 0.05:
            if current_div > 0:
                report["indicators"]["oi_price_divergence"]["description"] = (
                    f"Strong positive OI-price divergence ({current_div:.2f}) "
                )
            else:
                report["indicators"]["oi_price_divergence"]["description"] = (
                    f"Strong negative OI-price divergence ({current_div:.2f}) "
                )

            if abs(div_trend) > 0.001:
                report["indicators"]["oi_price_divergence"]["description"] += (
                    f"with {'increasing' if div_trend > 0 else 'decreasing'} trend. "
                )
        else:
            report["indicators"]["oi_price_divergence"]["description"] = (
                f"Neutral OI-price divergence ({current_div:.2f}). "
            )

    # 4. Long/Short Ratio Analysis with Recent Trend
    if "long_short_ratio" in recent_df.columns:
        current_ls = latest_row["long_short_ratio"]
        avg_ls = recent_df["long_short_ratio"].mean()
        ls_trend = recent_df["long_short_ratio"].diff().mean()

        extreme_counts = {
            "bullish": recent_df["extreme_bullish"].sum()
            if "extreme_bullish" in recent_df.columns
            else 0,
            "bearish": recent_df["extreme_bearish"].sum()
            if "extreme_bearish" in recent_df.columns
            else 0,
        }

        report["indicators"]["ls_ratio"] = {
            "current": current_ls,
            "average": avg_ls,
            "trend": ls_trend,
            "extreme_signals": extreme_counts,
            "description": f"L/S ratio is {current_ls:.2f} ",
        }

        if extreme_counts["bullish"] > 0 or extreme_counts["bearish"] > 0:
            report["indicators"]["ls_ratio"]["description"] += (
                f"with {extreme_counts['bullish']} bullish and {extreme_counts['bearish']} bearish extreme signals in recent periods. "
            )

        if abs(ls_trend) > 0.01:
            report["indicators"]["ls_ratio"]["description"] += (
                f"Ratio is trending {'up' if ls_trend > 0 else 'down'}. "
            )

        # Add z-score if available
        if "ls_ratio_z_score" in latest_row and not pd.isna(
            latest_row["ls_ratio_z_score"]
        ):
            report["indicators"]["ls_ratio"]["z_score"] = latest_row["ls_ratio_z_score"]
            report["indicators"]["ls_ratio"]["description"] += (
                f"Current z-score: {latest_row['ls_ratio_z_score']:.2f}. "
            )

    # 5. OI-Volume Ratio Trend
    if "oi_volume_ratio" in recent_df.columns:
        current_ratio = latest_row["oi_volume_ratio"]
        avg_ratio = recent_df["oi_volume_ratio"].mean()
        ratio_trend = recent_df["oi_volume_ratio"].diff().mean()

        report["indicators"]["oi_volume_ratio"] = {
            "current": current_ratio,
            "average": avg_ratio,
            "trend": ratio_trend,
            "description": f"OI/Volume ratio is {current_ratio:.2f} ",
        }

        if current_ratio > avg_ratio * 1.5:
            report["indicators"]["oi_volume_ratio"]["description"] += (
                "significantly above average, suggesting high accumulated positions. "
            )
        elif current_ratio < avg_ratio * 0.5:
            report["indicators"]["oi_volume_ratio"]["description"] += (
                "significantly below average, suggesting reduced position commitment. "
            )

    # Generate overall market summary considering trends
    bullish_signals = []
    bearish_signals = []
    neutral_signals = []

    # Add trend-based signals
    if "funding_rate" in recent_df.columns and funding_trend is not None:
        if funding_trend > 0 and current_funding > avg_funding:
            bullish_signals.append("increasing positive funding rates")
        elif funding_trend < 0 and current_funding < avg_funding:
            bearish_signals.append("decreasing negative funding rates")

    if "oi_price_divergence" in recent_df.columns and div_trend is not None:
        if div_trend > 0 and current_div > 0:
            bullish_signals.append("strengthening positive OI-price divergence")
        elif div_trend < 0 and current_div < 0:
            bearish_signals.append("strengthening negative OI-price divergence")

    # Add squeeze signals considering recent history
    if (
        "potential_short_squeeze" in recent_df.columns
        and "potential_long_squeeze" in recent_df.columns
    ):
        if (
            recent_short_squeezes > lookback_periods * 0.25
        ):  # If squeezes in >25% of recent periods
            bullish_signals.append(
                f"persistent short squeeze conditions ({recent_short_squeezes}/{lookback_periods} periods)"
            )
        if recent_long_squeezes > lookback_periods * 0.25:
            bearish_signals.append(
                f"persistent long squeeze conditions ({recent_long_squeezes}/{lookback_periods} periods)"
            )

    # Add L/S ratio signals
    if "long_short_ratio" in recent_df.columns and ls_trend is not None:
        if current_ls > 1.5 and ls_trend > 0:
            bullish_signals.append("high and increasing long/short ratio")
        elif current_ls < 0.8 and ls_trend < 0:
            bearish_signals.append("low and decreasing long/short ratio")

    # Add L/S extreme signals (as contrarian indicators)
    if "extreme_bullish" in recent_df.columns and latest_row.get(
        "extreme_bullish", False
    ):
        bearish_signals.append("extremely bullish positioning (contrarian)")
    if "extreme_bearish" in recent_df.columns and latest_row.get(
        "extreme_bearish", False
    ):
        bullish_signals.append("extremely bearish positioning (contrarian)")

    # Add OI/Volume signals
    if "oi_volume_ratio" in recent_df.columns:
        if current_ratio > avg_ratio * 2:
            bullish_signals.append("very high OI/Volume ratio")

    # Compile final summary
    sentiment = "neutral"
    if len(bullish_signals) > len(bearish_signals) + 1:
        sentiment = "bullish"
    elif len(bearish_signals) > len(bullish_signals) + 1:
        sentiment = "bearish"

    report["summary"] = (
        f"Market sentiment appears {sentiment} over the last {lookback_periods} periods. "
    )
    if bullish_signals:
        report["summary"] += f"Bullish signals: {', '.join(bullish_signals)}. "
    if bearish_signals:
        report["summary"] += f"Bearish signals: {', '.join(bearish_signals)}. "
    if neutral_signals:
        report["summary"] += f"Neutral signals: {', '.join(neutral_signals)}. "

    return report
