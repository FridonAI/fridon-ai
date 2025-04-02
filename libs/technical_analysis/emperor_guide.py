import pandas as pd
import pandas_ta as ta
from datetime import datetime


def detect_bullish_ema_crossover(
    df: pd.DataFrame, contraction_threshold: float = 0.001
) -> pd.DataFrame:
    df["EMA_13"] = ta.ema(df["Close"], length=13)
    df["EMA_21"] = ta.ema(df["Close"], length=21)

    df["EMA_13_prev"] = df["EMA_13"].shift(1)
    df["EMA_21_prev"] = df["EMA_21"].shift(1)

    df["CrossUp"] = (df["EMA_13_prev"] < df["EMA_21_prev"]) & (
        df["EMA_13"] > df["EMA_21"]
    )

    df["PriceAboveEMAs"] = (df["Close"] > df["EMA_13"]) & (df["Close"] > df["EMA_21"])

    if contraction_threshold is not None and contraction_threshold > 0:
        df["ema_diff_prev"] = (df["EMA_13_prev"] - df["EMA_21_prev"]).abs()
        df["ContractionBeforeCross"] = (
            df["ema_diff_prev"] / df["Close"].shift(1) < contraction_threshold
        ) & df["CrossUp"]
    else:
        df["ContractionBeforeCross"] = False

    df.drop(
        columns=["EMA_13_prev", "EMA_21_prev", "ema_diff_prev"],
        errors="ignore",
        inplace=True,
    )

    return df


def ema_up_slope_stopped_timestamp(
    df: pd.DataFrame, crossover_timestamp: int, window_size: int = 5
):
    # Filter data after crossover
    df_after_cross = df[df["Timestamp"] >= crossover_timestamp].copy()

    upsloping_condition = df_after_cross["EMA_13"] > df_after_cross["EMA_13"].shift(
        window_size
    )
    slope_stopped_mask = upsloping_condition.shift(1) & ~upsloping_condition

    if slope_stopped_mask.any():
        slope_stopped_index = df_after_cross.index[slope_stopped_mask].min()
        slope_stopped_timestamp = df_after_cross.loc[slope_stopped_index, "Timestamp"]
        return int(slope_stopped_timestamp)
    else:
        return None


def price_above_ema_stopped_timestamp(
    df: pd.DataFrame,
    crossover_timestamp: int,
    window_size: int = 5,
    max_consecutive_below: int = 2,
    max_violations_in_window: int = 2,
):
    df_after_cross = df[df["Timestamp"] >= crossover_timestamp].copy()

    from collections import deque

    consecutive_below = 0
    rolling_violations = deque()

    for i in range(len(df_after_cross)):
        if i > 0 and (
            df_after_cross["EMA_21"].iloc[i - 1] <= df_after_cross["EMA_13"].iloc[i - 1]
            and df_after_cross["EMA_21"].iloc[i] > df_after_cross["EMA_13"].iloc[i]
        ):
            return int(df_after_cross.loc[df_after_cross.index[i], "Timestamp"])

        if df_after_cross["Close"].iloc[i] < df_after_cross["EMA_13"].iloc[i]:
            consecutive_below += 1
            rolling_violations.append(1)
        else:
            consecutive_below = 0
            rolling_violations.append(0)

        if len(rolling_violations) > window_size:
            rolling_violations.popleft()

        if (consecutive_below > max_consecutive_below) or (
            sum(rolling_violations) > max_violations_in_window
        ):
            return int(df_after_cross.loc[df_after_cross.index[i], "Timestamp"])
    return None


def _timestamp_to_days(timestamp: int) -> str:
    return round(timestamp / (24 * 3600), 1)


def _timestamp_to_hours(timestamp: int) -> str:
    return round(timestamp / 3600, 1)


def get_latest_ema_crossover(
    df: pd.DataFrame, offset_timestamp: int = None
) -> pd.DataFrame:
    df = detect_bullish_ema_crossover(df)

    result = {}

    if df["CrossUp"].any():
        last_crossup_idx = df[df["CrossUp"]].index[-1]
        result["crossover_timestamp"] = int(df.loc[last_crossup_idx, "Timestamp"])
        result["crossover_datetime"] = datetime.fromtimestamp(
            result["crossover_timestamp"] // 1000,
        ).strftime("%Y-%m-%dT%H:%M:%S")
        result["since_crossover"] = (
            f"{_timestamp_to_days(df['Timestamp'].iloc[-1] - result['crossover_timestamp'])} days passed since crossover"
        )

        if (
            offset_timestamp is not None
            and result["crossover_timestamp"] < offset_timestamp
        ):
            return None
        result["up_slope_stopped_timestamp"] = ema_up_slope_stopped_timestamp(
            df, result["crossover_timestamp"]
        )

        if result["up_slope_stopped_timestamp"] is not None:
            result["up_slope_stopped_datetime"] = datetime.fromtimestamp(
                result["up_slope_stopped_timestamp"] // 1000
            ).strftime("%Y-%m-%dT%H:%M:%S")
            result["since_up_slope_stopped"] = (
                f"{_timestamp_to_days(df['Timestamp'].iloc[-1] - result['up_slope_stopped_timestamp'])} days passed since up slope stopped"
            )

        result["price_above_em_stopped_timestamp"] = price_above_ema_stopped_timestamp(
            df, result["crossover_timestamp"]
        )

        if result["price_above_em_stopped_timestamp"] is not None:
            result["price_above_em_stopped_datetime"] = datetime.fromtimestamp(
                result["price_above_em_stopped_timestamp"] // 1000
            ).strftime("%Y-%m-%dT%H:%M:%S")
            result["since_price_above_em_stopped"] = (
                f"{_timestamp_to_days(df['Timestamp'].iloc[-1] - result['price_above_em_stopped_timestamp'])} days passed since price above EMAs stopped"
            )
        return result

    return None


def check_200ema_support(
    df: pd.DataFrame,
    threshold: float = 0.01,
    ema_crossover_timestamp: int | None = None,
) -> pd.DataFrame:
    df["EMA_200"] = ta.ema(df["Close"], length=200)

    tested_ema_200_condition = (
        (df["Low"] <= df["EMA_200"] * (1 + threshold))
        & (df["Low"] >= df["EMA_200"] * (1 - threshold))
        & (df["Close"] > df["EMA_200"])
    )

    if tested_ema_200_condition.any():
        if ema_crossover_timestamp is None:
            last_support_idx = df[tested_ema_200_condition].index[-1]
            support_timestamp = df.loc[last_support_idx, "Timestamp"]
            return {
                "support_timestamp": int(support_timestamp),
                "support_datetime": datetime.fromtimestamp(
                    support_timestamp // 1000
                ).strftime("%Y-%m-%dT%H:%M:%S"),
                "since_support": f"{_timestamp_to_hours(df['Timestamp'].iloc[-1] - support_timestamp)} hours passed since support",
            }
        else:
            crossover_idx = df[df["Timestamp"] == ema_crossover_timestamp].index[0]
            support_after_cross = df.loc[crossover_idx:][tested_ema_200_condition]
            if not support_after_cross.empty:
                first_support_idx = support_after_cross.index[0]
                return {
                    "support_timestamp": int(df.loc[first_support_idx, "Timestamp"]),
                    "support_datetime": datetime.fromtimestamp(
                        df.loc[first_support_idx, "Timestamp"] // 1000
                    ).strftime("%Y-%m-%dT%H:%M:%S"),
                    "since_support": f"{_timestamp_to_hours(df['Timestamp'].iloc[-1] - df.loc[first_support_idx, 'Timestamp'])} hours passed since support",
                }
    return None
