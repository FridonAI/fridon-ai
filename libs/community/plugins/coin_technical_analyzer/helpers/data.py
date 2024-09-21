import asyncio
import json
from datetime import datetime

import aiohttp
import pandas as pd
import pandas_ta as ta


def read_token_list(token_list_path) -> list[dict]:
    with open(token_list_path) as f:
        return json.load(f)


async def read_token_summary(
    session: aiohttp.ClientSession, symbol: str
) -> dict | None:
    try:
        async with session.get(
            f"https://api.kraken.com/0/public/OHLC?pair={symbol.upper()}USD&interval=1440&since={int(datetime.now().timestamp() - 120 * 24 * 60 * 60)}"
        ) as resp:
            response_data = await resp.json()

            if resp.status != 200 or len(response_data["error"]) > 0:
                raise Exception(
                    f"Failed to fetch data from Kraken API. Status code: {resp.status}"
                )

            data = list(response_data["result"].values())[0]
            df = pd.DataFrame(
                data,
                columns=[
                    "time",
                    "open",
                    "high",
                    "low",
                    "close",
                    "vwap",
                    "volume",
                    "count",
                ],
            )
            df.drop(columns=["vwap", "count"], inplace=True)
            df.rename(columns={"time": "date"}, inplace=True)
            df["date"] = pd.to_datetime(df["date"], unit="s")
            df["open"] = df["open"].astype(float)
            df["high"] = df["high"].astype(float)
            df["low"] = df["low"].astype(float)
            df["close"] = df["close"].astype(float)
            df["volume"] = df["volume"].astype(float)
            df.set_index("date", inplace=True)
            df = df.iloc[:-1]
            df.ta.macd(append=True)
            df.ta.rsi(append=True)
            df.ta.bbands(append=True)
            df.ta.obv(append=True)

            df.ta.sma(length=20, append=True)
            df.ta.ema(length=50, append=True)
            df.ta.stoch(append=True)
            df.ta.adx(append=True)

            df.ta.willr(append=True)
            df.ta.cmf(append=True)
            df.ta.psar(append=True)

            df["OBV_in_million"] = df["OBV"] / 1e7
            df["MACD_histogram_12_26_9"] = df["MACDh_12_26_9"]

            last_day_summary = df.iloc[-1][
                [
                    "close",
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
            return {"last_day_summary": str(last_day_summary), "symbol": symbol}

    except Exception:
        return None


async def read_token_summary_list(token_list: list[dict]) -> list[dict]:
    batch_size = 10
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(0, len(token_list), batch_size):
            batch = token_list[i : i + batch_size]

            tasks.append(
                asyncio.gather(
                    *[read_token_summary(session, token["symbol"]) for token in batch]
                )
            )
        results = await asyncio.gather(*tasks)
        return [item for sublist in results for item in sublist if item is not None]
