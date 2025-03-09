import os
import aiohttp
from typing import List, Literal, Dict, Union, Any
from datetime import UTC, datetime, timedelta

from libs.data_providers.ohlcv.base import BaseOHLCVProvider
from libs.data_providers.token_providers import JupiterTokenListDataProvider


class BirdeyeOHLCVProvider(BaseOHLCVProvider):
    _batch_size = 15

    def __init__(self, token_list):
        self._base_url = "https://public-api.birdeye.so"
        self._birdeye_api_key = os.getenv("BIRDEYE_API_KEY")
        self._token_map = {
            token["symbol"].upper().lstrip("$"): token for token in token_list
        }
        self._interval_map = {
            "30m": "30m",
            "1h": "1H",
            "4h": "4H",
            "1d": "1D",
            "1w": "1W",
        }

        self.interval_deltas = {
            "30m": timedelta(minutes=30),
            "1h": timedelta(hours=1),
            "4h": timedelta(hours=4),
            "1d": timedelta(days=1),
            "1w": timedelta(weeks=1),
        }

    @staticmethod
    async def create():
        token_list_provider = JupiterTokenListDataProvider()
        token_list = await token_list_provider.get_token_list()
        return BirdeyeOHLCVProvider(token_list)

    async def get_historical_ohlcv_by_start_end(
        self,
        symbols: List[str],
        interval: Literal["30m", "1h", "4h", "1d", "1w"] = "30m",
        start_time: Union[datetime, None] = None,
        end_time: Union[datetime, None] = None,
        output_format: Literal["dataframe", "dict"] = "dataframe",
        category: Literal["spot", "futures"] = "spot",
    ):
        if not start_time or not end_time:
            raise ValueError("start_time and end_time must be provided")

        results = await self._fetch_ohlcv_for_coins(
            symbols, interval, start_time, end_time
        )
        all_data = [entry for coin_data in results for entry in coin_data]

        if output_format == "dataframe":
            return self._to_dataframe(all_data)
        return all_data

    async def get_historical_ohlcv_by_start_end_for_address(
        self,
        address: str,
        interval: Literal["30m", "1h", "4h", "1d", "1w"] = "30m",
        start_time: Union[datetime, None] = None,
        end_time: Union[datetime, None] = None,
        output_format: Literal["dataframe", "dict"] = "dataframe",
        category: Literal["spot", "futures"] = "spot",
    ):
        if not start_time or not end_time:
            raise ValueError("start_time and end_time must be provided")

        interval_key = self._interval_map.get(interval, "30m")
        params = {
            "address": address,
            "type": interval_key,
            "time_from": int(start_time.timestamp()),
            "time_to": int(end_time.timestamp()),
        }
        data = await self._fetch_coin_ohlcv_birdeye(None, params)

        if output_format == "dataframe":
            return self._to_dataframe(data)
        return data

    async def get_historical_ohlcv(
        self,
        symbols: List[str],
        interval: str = "30m",
        days: int = 45,
        output_format: str = "dict",
        category: Literal["spot", "futures"] = "spot",
    ):
        end_time = datetime.now(UTC)
        start_time = end_time - timedelta(days=days)

        return await self.get_historical_ohlcv_by_start_end(
            symbols, interval, start_time, end_time, output_format
        )

    async def get_historical_ohlcv_for_address(
        self,
        address: str,
        interval: Literal["30m", "1h", "4h", "1d", "1w"] = "30m",
        days: int = 45,
        output_format: Literal["dataframe", "dict"] = "dataframe",
    ):
        end_time = datetime.now(UTC)
        start_time = end_time - timedelta(days=days)

        return await self.get_historical_ohlcv_by_start_end_for_address(
            address, interval, start_time, end_time, output_format
        )

    async def get_current_ohlcv(
        self,
        symbols: List[str],
        interval: Literal["30m", "1h", "4h", "1d", "1w"] = "30m",
        output_format: Literal["dataframe", "dict"] = "dataframe",
    ):
        time_to = datetime.now(UTC)
        time_from = time_to - self.interval_deltas.get(interval, timedelta(minutes=30))

        results = await self._fetch_ohlcv_for_coins(
            symbols, interval, time_from, time_to
        )
        latest_data = [res[-1] for res in results if res]

        if output_format == "dataframe":
            return self._to_dataframe(latest_data)
        return latest_data

    async def _fetch_ohlcv_for_coins(
        self,
        symbols: List[str],
        interval: Literal["30m", "1h", "4h", "1d", "1w"],
        time_from: datetime,
        time_to: datetime,
    ) -> list[list[dict]]:
        interval_key = self._interval_map.get(interval, "30m")
        tasks = []
        for symbol in symbols:
            symbol = symbol.upper()
            token = self._token_map.get(symbol)
            if not token:
                continue
            params = {
                "address": token["address"],
                "type": interval_key,
                "time_from": int(time_from.timestamp()),
                "time_to": int(time_to.timestamp()),
            }
            tasks.append(self._fetch_coin_ohlcv_birdeye(symbol, params))
        results = await self._execute_in_batches(tasks)
        return results

    async def _fetch_coin_ohlcv_birdeye(
        self, symbol: str | None, params: Dict
    ) -> List[Dict[str, Any]]:
        formatted_data = []
        headers = {
            "accept": "application/json",
            "x-chain": "solana",
            "X-API-KEY": self._birdeye_api_key,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self._base_url}/defi/ohlcv", params=params, headers=headers
                ) as resp:
                    response_data = await resp.json()
        except Exception as e:
            identifier = symbol if symbol is not None else params.get("address")
            print(f"Error fetching data for {identifier} with params {params}: {e}")
            return []

        if not response_data.get("success") or response_data.get("data") is None:
            return []

        for entry in response_data["data"]["items"]:
            timestamp = entry.get("unixTime")
            if not timestamp:
                continue
            date_str = datetime.fromtimestamp(timestamp, UTC).strftime("%Y-%m-%d")

            if symbol is None:
                symbol = await self._get_ca_symbol_birdeye(entry.get("address"))
            formatted_data.append(
                {
                    "coin": symbol,
                    "timestamp": timestamp * 1000,
                    "date": date_str,
                    "open": entry.get("o"),
                    "high": entry.get("h"),
                    "low": entry.get("l"),
                    "close": entry.get("c"),
                    "volume": entry.get("v"),
                }
            )
        return formatted_data

    async def _get_ca_symbol_birdeye(self, address: str) -> str:
        headers = {
            "accept": "application/json",
            "x-chain": "solana",
            "X-API-KEY": self._birdeye_api_key,
        }
        params = {"address": address}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self._base_url}/defi/v3/token/meta-data/single",
                    params=params,
                    headers=headers,
                ) as resp:
                    response_data = await resp.json()
                    if (
                        not response_data.get("success")
                        or response_data.get("data") is None
                    ):
                        return address
                    return response_data["data"]["symbol"]
        except Exception as e:
            print("Error while fetching CA symbol:", e)
            return address
