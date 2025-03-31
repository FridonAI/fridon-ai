import pandas as pd
import polars as pl
import pandas_ta as ta

def calculate_ta_indicators(
    df: pl.DataFrame | pd.DataFrame, return_last_one: bool = True
) -> pl.DataFrame:
    if isinstance(df, pl.DataFrame):
        df_pandas = df.to_pandas()
    else:
        df_pandas = df

    if "date" in df_pandas.columns:
        df_pandas = df_pandas.drop(columns=["date"])

    df_pandas.rename(columns={"timestamp": "date"}, inplace=True)
    coin = df_pandas["coin"].iloc[0]
    df_pandas.drop(columns=["coin"], inplace=True)
    df_pandas["date"] = pd.to_datetime(df_pandas["date"], unit="ms")
    numeric_columns = ["open", "high", "low", "close", "volume"]
    df_pandas[numeric_columns] = df_pandas[numeric_columns].astype(float)

    # Try to calculate each indicator, set to None if fails
    try:
        df_pandas.ta.macd(append=True)
        df_pandas["MACD_histogram_12_26_9"] = df_pandas["MACDh_12_26_9"]
    except:
        df_pandas["MACD_12_26_9"] = None
        df_pandas["MACDh_12_26_9"] = None
        df_pandas["MACD_histogram_12_26_9"] = None

    try:
        df_pandas.ta.rsi(append=True)
    except:
        df_pandas["RSI_14"] = None

    try:
        df_pandas.ta.bbands(append=True)
    except:
        df_pandas["BBL_5_2.0"] = None
        df_pandas["BBM_5_2.0"] = None
        df_pandas["BBU_5_2.0"] = None

    try:
        df_pandas.ta.obv(append=True)
    except:
        df_pandas["OBV"] = None

    try:
        df_pandas.ta.sma(length=20, append=True)
    except:
        df_pandas["SMA_20"] = None

    try:
        df_pandas.ta.ema(length=50, append=True)
    except:
        df_pandas["EMA_50"] = None

    try:
        df_pandas.ta.stoch(append=True)
    except:
        df_pandas["STOCHk_14_3_3"] = None
        df_pandas["STOCHd_14_3_3"] = None

    try:
        df_pandas.ta.adx(append=True)
    except:
        df_pandas["ADX_14"] = None

    try:
        df_pandas.ta.willr(append=True)
    except:
        df_pandas["WILLR_14"] = None

    try:
        df_pandas.ta.cmf(append=True)
    except:
        df_pandas["CMF_20"] = None

    try:
        df_pandas.ta.psar(append=True)
    except:
        df_pandas["PSARl_0.02_0.2"] = None
        df_pandas["PSARs_0.02_0.2"] = None

    df_pandas["OBV_in_million"] = (
        df_pandas["OBV"].div(1e7) if df_pandas["OBV"] is not None else None
    )

    if not return_last_one:
        if df_pandas.shape[0] > 80:
            df_pandas = df_pandas.iloc[49:]
        df_pandas = df_pandas.assign(coin=coin)
        df_pandas["timestamp"] = df_pandas["date"].apply(lambda x: int(x.timestamp() * 1000))
        df_pandas["date"] = df_pandas["date"].apply(lambda x: x.strftime("%Y-%m-%d"))
        return pl.from_pandas(df_pandas)

    last_record = df_pandas.iloc[-1][
        [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "MACD_12_26_9",
            "MACD_histogram_12_26_9",
            "RSI_14",
            "BBL_5_2.0",
            "BBM_5_2.0",
            "BBU_5_2.0",
            "SMA_20",
            "EMA_50",
            "OBV_in_million",
            "STOCHk_14_3_3",
            "STOCHd_14_3_3",
            "ADX_14",
            "WILLR_14",
            "CMF_20",
            "PSARl_0.02_0.2",
            "PSARs_0.02_0.2",
        ]
    ]
    non_numeric_columns = pd.Series(
        {
            "coin": coin,
            "timestamp": int(df_pandas["date"].iloc[-1].timestamp() * 1000),
            "date": df_pandas["date"].iloc[-1].strftime("%Y-%m-%d"),
        }
    )
    combined_summary = pd.concat([last_record, non_numeric_columns])
    return pl.from_pandas(combined_summary.to_frame().T)