import aiohttp
import asyncio
import pandas as pd
from datetime import datetime, timedelta, UTC
from typing import List, Literal, Union, Dict, Any

from libs.data_providers.ohlcv.base import BaseOHLCVProvider


class BinanceOHLCVProvider(BaseOHLCVProvider):
    """
    Binance implementation of the coin price data provider.
    Fetches data from Binance API.
    """

    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.base_futures_url = "https://fapi.binance.com/fapi/v1"
        self.klines_endpoint = "/klines"

        self._batch_size = 20
        self._request_delay = 0.5
        self._max_limit = 500  # Binance API max limit per call

    async def get_historical_ohlcv(
        self,
        symbols: List[str],
        interval: Literal["1h", "4h", "1d", "1w"],
        days: int = 45,
        output_format: Literal["dataframe", "dict"] = "dataframe",
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
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
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)
        all_data = []
        tasks = []

        async with aiohttp.ClientSession() as session:
            tasks = list(
                map(
                    lambda symbol: asyncio.create_task(
                        self._fetch_symbol_data(
                            session, symbol, interval, start_timestamp, end_timestamp
                        )
                    ),
                    symbols,
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
        self, symbols: List[str], interval: Literal["1h", "4h", "1d", "1w"]
    ) -> List[Dict[str, Any]]:
        tasks = []
        async with aiohttp.ClientSession() as session:
            tasks = list(
                map(
                    lambda symbol: asyncio.create_task(
                        self._fetch_current_data(session, symbol, interval)
                    ),
                    symbols,
                )
            )
            results = await asyncio.gather(*tasks)
        return [item for sublist in results for item in sublist]

    async def _fetch_symbol_data(
        self,
        session: aiohttp.ClientSession,
        symbol: str,
        interval: str,
        start_timestamp: int,
        end_timestamp: int,
    ) -> List[Dict[str, Any]]:
        """Fetches historical OHLCV data with pagination."""
        all_data = []
        # Ensure symbol has the USDT pair
        symbol_pair = f"{symbol}USDT" if not symbol.endswith("USDT") else symbol
        current_start = start_timestamp

        while True:
            params = {
                "symbol": symbol_pair,
                "interval": interval,
                "startTime": current_start,
                "endTime": end_timestamp,
                "limit": self._max_limit,
            }
            try:
                async with session.get(
                    f"{self.base_url}{self.klines_endpoint}", params=params
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        print(f"Failed to fetch data for {symbol_pair}: {error_text}")
                        break
                    data = await resp.json()
            except Exception as e:
                print(f"Error fetching {symbol_pair} data: {e}")

            if not data:
                break

            for candle in data:
                all_data.append(
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

            if len(data) < self._max_limit:
                break

            current_start = data[-1][0] + 1

        return all_data

    async def _fetch_current_data(
        self,
        session: aiohttp.ClientSession,
        symbol: str,
        interval: Literal["1h", "4h", "1d", "1w"],
    ) -> List[Dict[str, Any]]:
        """Fetches the latest single OHLCV data point."""
        symbol_pair = f"{symbol}USDT" if not symbol.endswith("USDT") else symbol
        params = {"symbol": symbol_pair, "interval": interval, "limit": 1}
        async with session.get(
            f"{self.base_url}{self.klines_endpoint}", params=params
        ) as response:
            if response.status != 200:
                print(
                    f"Failed to fetch current data for {symbol_pair}: {await response.text()}"
                )
                return []
            data = await response.json()

        result = []
        for candle in data:
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
