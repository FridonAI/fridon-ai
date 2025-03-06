import aiohttp
import pandas as pd
import polars as pl
import asyncio
from datetime import datetime, timedelta, UTC
from typing import List, Literal, Union, Dict, Any

from libs.data_providers.ohlcv.base import BaseOHLCVProvider


class BybitOHLCVProvider(BaseOHLCVProvider):
    """
    Bybit V5 implementation of an OHLCV data provider.

    This provider uses the new unified V5 REST API endpoint `/v5/market/kline`
    to fetch historical and current candle data for a given list of symbols.

    """

    def __init__(self):
        self.base_url = "https://api.bybit.com"
        self.klines_endpoint = "/v5/market/kline"
        self._batch_size = 20
        self._request_delay = 0.5
        self._max_limit = 1000  # Bybit V5 allows up to 1000 candles per request.

        self.INTERVAL_MAPPING = {
            "1h": "60",
            "4h": "240",
            "1d": "D",
            "1w": "W",
        }
        # For this provider we assume the "spot" market category.
        self.category = "spot"

    async def get_historical_ohlcv(
        self,
        symbols: List[str],
        interval: Literal["1h", "4h", "1d", "1w"] = "1h",
        days: int = 45,
        output_format: Literal["dataframe", "dict"] = "dataframe",
    ) -> Union[pl.DataFrame, List[Dict[str, Any]]]:
        end_time = datetime.now(UTC)
        start_time = end_time - timedelta(days=days)
        return await self.get_historical_ohlcv_by_start_end(
            symbols, interval, start_time, end_time, output_format
        )

    async def get_historical_ohlcv_by_start_end(
        self,
        symbols: List[str],
        interval: Literal["1h", "4h", "1d", "1w"],
        start_time: datetime,
        end_time: datetime,
        output_format: Literal["dataframe", "dict"] = "dataframe",
    ) -> Union[pl.DataFrame, List[Dict[str, Any]]]:
        start_ts = int(start_time.timestamp()) * 1000
        end_ts = int(end_time.timestamp()) * 1000

        all_data = []
        tasks = []
        async with aiohttp.ClientSession() as session:
            for symbol in symbols:
                tasks.append(
                    asyncio.create_task(
                        self._fetch_symbol_data(
                            session, symbol, interval, start_ts, end_ts
                        )
                    )
                )

            for batch in await self._execute_in_batches(tasks):
                all_data.extend(batch)

        if output_format == "dataframe":
            if not all_data:
                return pd.DataFrame()
            return pd.DataFrame(all_data)
        return all_data

    async def get_current_ohlcv(
        self,
        symbols: List[str],
        interval: Literal["1h", "4h", "1d", "1w"] = "1h",
    ) -> List[Dict[str, Any]]:
        """
        Fetch the current (latest) candle for each symbol.
        Computes the current candle’s open time based on UTC time.
        """
        tasks = []
        async with aiohttp.ClientSession() as session:
            for symbol in symbols:
                tasks.append(
                    asyncio.create_task(
                        self._fetch_current_data(session, symbol, interval)
                    )
                )
            results = await asyncio.gather(*tasks)
        return [item for sublist in results for item in sublist]

    async def _fetch_symbol_data(
        self,
        session: aiohttp.ClientSession,
        symbol: str,
        interval: str,
        start_ts: int,
        end_ts: int,
    ) -> List[Dict[str, Any]]:
        """
        Fetches historical OHLCV data for a given symbol via the V5 API endpoint.
        Implements pagination by updating the "start" parameter.
        """
        all_data = []

        symbol_pair = f"{symbol}USDT" if not symbol.endswith("USDT") else symbol
        interval_str = self.INTERVAL_MAPPING.get(interval, interval)
        current_end = end_ts

        while True:
            params = {
                "category": self.category,
                "symbol": symbol_pair,
                "interval": interval_str,
                "start": start_ts,
                "end": current_end,
                "limit": self._max_limit,
            }
            url = f"{self.base_url}{self.klines_endpoint}"
            try:
                async with session.get(url, params=params) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        print(f"Error fetching {symbol_pair} data: {error_text}")
                        break
                    data = await resp.json()
            except Exception as e:
                print(f"Error fetching {symbol_pair} data: {e}")
                break

            if data.get("retCode", 0) != 0:
                print(f"Error fetching {symbol_pair} data: {data.get('retMsg')}")
                break

            candles = data.get("result", {}).get("list", [])
            if not candles:
                break

            for candle in candles:
                all_data.append(
                    {
                        "coin": symbol_pair.replace("USDT", ""),
                        "timestamp": int(candle[0]),
                        "open": float(candle[1]),
                        "high": float(candle[2]),
                        "low": float(candle[3]),
                        "close": float(candle[4]),
                        "volume": float(candle[5]),
                    }
                )

            if len(candles) < self._max_limit:
                break

            current_end = int(candles[-1][0]) - 1

            if current_end < start_ts:
                break

        return reversed(all_data)

    async def _fetch_current_data(
        self,
        session: aiohttp.ClientSession,
        symbol: str,
        interval: str,
    ) -> List[Dict[str, Any]]:
        """
        Fetches the latest candle for a given symbol.
        Computes the current candle’s open time and requests a single candle.
        """
        interval_str = self.INTERVAL_MAPPING.get(interval, interval)
        symbol_pair = f"{symbol}USDT" if not symbol.endswith("USDT") else symbol

        params = {
            "category": self.category,
            "symbol": symbol_pair,
            "interval": interval_str,
            "limit": 1,
        }
        url = f"{self.base_url}{self.klines_endpoint}"
        try:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    print(
                        f"Error fetching current data for {symbol_pair}: {error_text}"
                    )
                    return []
                data = await resp.json()
        except Exception as e:
            print(f"Error fetching current data for {symbol_pair}: {e}")
            return []

        if data.get("retCode", 0) != 0:
            print(
                f"Error fetching current data for {symbol_pair}: {data.get('retMsg')}"
            )
            return []

        candles = data.get("result", {}).get("list", [])
        result = []
        for candle in candles:
            result.append(
                {
                    "coin": symbol_pair.replace("USDT", ""),
                    "timestamp": candle[0],
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[5]),
                }
            )
        return result
