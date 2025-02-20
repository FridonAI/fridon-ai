import asyncio
import os
import random
from datetime import UTC, datetime, timedelta
import json
from pathlib import Path

import aiohttp
import pandas as pd

from libs.data_providers.token_providers import JupiterTokenListDataProvider


class CoinPriceDataProvider:
    async def get_current_ohlcv(self, coins, interval, output_format): ...

    async def get_historical_ohlcv(self, coins, interval, days, output_format): ...

    def _to_dataframe(self, data: list[dict]) -> pd.DataFrame:
        if not data:
            return pd.DataFrame()
        columns = [
            "coin",
            "timestamp",
            "date",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
        df = pd.DataFrame(data, columns=columns)
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)
        return df

    async def _execute_in_batches(self, tasks: list[asyncio.Future]) -> list:
        results = []
        for i in range(0, len(tasks), self.BATCH_SIZE):
            batch = tasks[i : i + self.BATCH_SIZE]
            batch_results = await asyncio.gather(*batch)
            results.extend(batch_results)
            if i + self.BATCH_SIZE < len(tasks):
                await asyncio.sleep(1)
        return results


class DummyCoinPriceDataProvider(CoinPriceDataProvider):
    async def get_current_ohlcv(self, coins, interval="30m", output_format="dict"):
        return self._generate_coin_price_data_mock(coins)

    async def get_historical_ohlcv(
        self, coins, interval="30m", days=45, output_format="dict"
    ):
        print("Dummy data not implemented for historical ohlcv")
        pass

    def _generate_coin_price_data_mock(self, coins, current_time=None):
        data = []
        if current_time is None:
            current_time = datetime.now(UTC).replace(microsecond=0)
        timestamp = int(current_time.timestamp() * 1000)
        date_str = current_time.strftime("%Y-%m-%d")
        for coin in coins:
            open_price = random.uniform(1000, 50000)
            close_price = open_price + random.uniform(-500, 500)
            high_price = max(open_price, close_price) + random.uniform(0, 500)
            low_price = min(open_price, close_price) - random.uniform(0, 500)
            volume = random.uniform(100, 10000)
            data.append(
                {
                    "coin": coin,
                    "timestamp": timestamp,
                    "date": date_str,
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "close": close_price,
                    "volume": volume,
                }
            )
        return data, current_time


class BinanceCoinPriceDataProvider(CoinPriceDataProvider):
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3/klines"

    async def get_current_ohlcv(self, coins, interval="30m", output_format="dict"):
        return await self._generate_coins_price_data_binance(
            coins, interval, output_format=output_format
        )

    async def get_historical_ohlcv(
        self, coins, interval="30m", days=45, output_format="dict"
    ):
        return await self._generate_historical_coins_price_data_binance(
            coins, interval, days, output_format=output_format
        )

    async def get_historical_ohlcv_by_start_end(
        self, coins, interval, start_time, end_time, output_format="dataframe"
    ):
        return await self._generate_multiple_coins_price_data(
            coins,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            output_format=output_format,
        )

    async def _fetch_coin_ohlcv_binance(
        self, symbol, interval, days=None, limit=1, start_time=None, end_time=None
    ):
        formatted_data = []

        if days is not None or (start_time is not None and end_time is not None):
            if start_time is None:
                start_time = int(
                    (datetime.now(UTC) - timedelta(days=days)).timestamp() * 1000
                )

            while True:
                url = f"{self.base_url}?symbol={symbol}USDT&interval={interval}&startTime={start_time}&limit=500"
                if end_time:
                    url += f"&endTime={end_time}"
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url) as resp:
                            data = await resp.json()
                            if "code" in data and data["code"] in [-1121, -1100]:
                                return []
                except Exception as e:
                    print(f"Error fetching {symbol} {interval} data from Binance: {e}")
                    return []

                if not data:
                    break

                for entry in data:
                    timestamp = int(entry[0])
                    date_str = datetime.fromtimestamp(timestamp // 1000).strftime(
                        "%Y-%m-%d"
                    )
                    formatted_data.append(
                        {
                            "coin": symbol,
                            "timestamp": timestamp,
                            "date": date_str,
                            "open": float(entry[1]),
                            "high": float(entry[2]),
                            "low": float(entry[3]),
                            "close": float(entry[4]),
                            "volume": float(entry[5]),
                        }
                    )

                if len(data) < 500:
                    break

                start_time = data[-1][0] + 1
                await asyncio.sleep(0.1)

        else:
            url = f"{self.base_url}?symbol={symbol}USDT&interval={interval}&endTime={end_time}&limit={limit}"

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        data = await resp.json()
                        if "code" in data and data["code"] in [-1121, -1100]:
                            return []
            except Exception as e:
                print(f"Error fetching {symbol} {interval} data from Binance: {e}")
                return []

            for entry in data:
                timestamp = int(entry[0])
                date_str = datetime.fromtimestamp(timestamp // 1000).strftime(
                    "%Y-%m-%d"
                )
                formatted_data.append(
                    {
                        "coin": symbol,
                        "timestamp": timestamp,
                        "date": date_str,
                        "open": float(entry[1]),
                        "high": float(entry[2]),
                        "low": float(entry[3]),
                        "close": float(entry[4]),
                        "volume": float(entry[5]),
                    }
                )

        return formatted_data

    async def _generate_multiple_coins_price_data(
        self,
        coins,
        interval="30m",
        days=None,
        batch_size=10,
        output_format="dict",
        start_time=None,
        end_time=None,
    ):
        data = []
        tasks = []
        now = datetime.now(UTC)

        if start_time is not None and end_time is not None:
            start_time = int(start_time.timestamp() * 1000)
            end_time = int(end_time.timestamp() * 1000)
        else:
            if now.minute >= 30:
                end_time = now.replace(minute=30, second=0, microsecond=0)
            else:
                end_time = now.replace(minute=0, second=0, microsecond=0)
            end_time = int(end_time.timestamp() * 1000) - 1
            readable_end_time = datetime.fromtimestamp(end_time / 1000, UTC).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            print(f"Fetching latest coin prices before {readable_end_time}")
        for i, symbol in enumerate(coins):
            tasks.append(
                self._fetch_coin_ohlcv_binance(
                    symbol,
                    interval,
                    days=days,
                    start_time=start_time,
                    end_time=end_time,
                )
            )
            if (i + 1) % batch_size == 0:
                result = await asyncio.gather(*tasks)
                for coin_data in result:
                    data.extend(coin_data)
                tasks = []
                await asyncio.sleep(0.1)

        if tasks:
            result = await asyncio.gather(*tasks)
            for coin_data in result:
                data.extend(coin_data)

        if output_format == "dataframe":
            columns = [
                "coin",
                "timestamp",
                "date",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ]
            df = pd.DataFrame.from_records(data, columns=columns)
            df["open"] = df["open"].astype(float)
            df["high"] = df["high"].astype(float)
            df["low"] = df["low"].astype(float)
            df["close"] = df["close"].astype(float)
            df["volume"] = df["volume"].astype(float)

            return df

        return data, datetime.now(UTC).replace(microsecond=0)

    async def _generate_coins_price_data_binance(
        self, coins, interval="30m", output_format="dict"
    ):
        return await self._generate_multiple_coins_price_data(
            coins, interval, output_format=output_format
        )

    async def _generate_historical_coins_price_data_binance(
        self, coins, interval="30m", days=45, output_format="dict"
    ):
        return await self._generate_multiple_coins_price_data(
            coins, interval, days=days, batch_size=5, output_format=output_format
        )

class BirdeyeCoinPriceDataProvider(CoinPriceDataProvider):
    CACHE_DIR = Path("../../cache")
    CACHE_FILE = CACHE_DIR / "token_list_cache.json"
    CACHE_DURATION = timedelta(days=1)
    BATCH_SIZE = 15

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
            "1h": timedelta(hours=1),
            "4h": timedelta(hours=4),
            "1d": timedelta(days=1),
            "1w": timedelta(weeks=1),
        }

    @staticmethod
    async def create():
        token_list = await BirdeyeCoinPriceDataProvider._get_cached_token_list()
        return BirdeyeCoinPriceDataProvider(token_list)

    @staticmethod
    async def _get_cached_token_list():
        BirdeyeCoinPriceDataProvider.CACHE_DIR.mkdir(exist_ok=True)
        if BirdeyeCoinPriceDataProvider.CACHE_FILE.exists():
            with open(BirdeyeCoinPriceDataProvider.CACHE_FILE, "r") as f:
                cache_data = json.load(f)
                cache_time = datetime.fromtimestamp(cache_data["timestamp"], UTC)
                if (
                    datetime.now(UTC) - cache_time
                    < BirdeyeCoinPriceDataProvider.CACHE_DURATION
                ):
                    return cache_data["token_list"]

        token_list_provider = JupiterTokenListDataProvider()
        token_list = await token_list_provider.get_token_list()

        cache_data = {
            "timestamp": datetime.now(UTC).timestamp(),
            "token_list": token_list,
        }
        with open(BirdeyeCoinPriceDataProvider.CACHE_FILE, "w") as f:
            json.dump(cache_data, f)

        return token_list

    async def get_current_ohlcv(self, coins, interval: str = "30m", output_format: str = "dict"):
        time_to = datetime.now(UTC)
        time_from = time_to - self.interval_deltas.get(interval, timedelta(minutes=30))

        results = await self._fetch_ohlcv_for_coins(coins, interval, time_from, time_to)
        latest_data = [res[-1] for res in results if res]

        timestamp = datetime.now(UTC).replace(microsecond=0)
        if output_format == "dataframe":
            return self._to_dataframe(latest_data), timestamp
        return latest_data, timestamp

    async def get_historical_ohlcv_by_start_end(
        self,
        coins,
        interval: str = "30m",
        start_time: datetime = None,
        end_time: datetime = None,
        output_format: str = "dict",
    ):
        if not start_time or not end_time:
            raise ValueError("start_time and end_time must be provided")

        results = await self._fetch_ohlcv_for_coins(
            coins, interval, start_time, end_time
        )
        all_data = [entry for coin_data in results for entry in coin_data]

        if output_format == "dataframe":
            return self._to_dataframe(all_data)
        return all_data, datetime.now(UTC).replace(microsecond=0)

    async def get_historical_ohlcv_by_start_end_for_address(
        self,
        address: str,
        interval: str = "30m",
        start_time: datetime = None,
        end_time: datetime = None,
        output_format: str = "dict",
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
        self, coins, interval: str = "30m", days: int = 45, output_format: str = "dict"
    ):
        end_time = datetime.now(UTC)
        start_time = end_time - timedelta(days=days)

        return await self.get_historical_ohlcv_by_start_end(
            coins, interval, start_time, end_time, output_format
        )

    async def get_historical_ohlcv_for_address(
        self,
        address: str,
        interval: str = "30m",
        days: int = 45,
        output_format: str = "dict",
    ):
        end_time = datetime.now(UTC)
        start_time = end_time - timedelta(days=days)

        return await self.get_historical_ohlcv_by_start_end_for_address(
            address, interval, start_time, end_time, output_format
        )

    async def _fetch_ohlcv_for_coins(
        self,
        coins: list[str],
        interval: str,
        time_from: datetime,
        time_to: datetime,
    ) -> list[list[dict]]:
        interval_key = self._interval_map.get(interval, "30m")
        tasks = []
        for symbol in coins:
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
        self, symbol: str | None, params: dict
    ) -> list[dict]:
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

        params = {
            "address": address,
        }

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


class CompositeCoinPriceDataProvider(CoinPriceDataProvider):
    def __init__(self, providers: list[CoinPriceDataProvider]):
        self.providers = providers

    async def get_current_ohlcv(self, coins, interval, output_format):
        for provider in self.providers:
            resp = await provider.get_current_ohlcv(coins, interval, output_format)
            if isinstance(resp, tuple) or len(resp) > 0:
                return resp
        return [], datetime.now(UTC).replace(microsecond=0)


    async def get_historical_ohlcv(self, coins, interval, days, output_format):
        for provider in self.providers:
            resp = await provider.get_historical_ohlcv(
                coins, interval, days, output_format
            )
            if isinstance(resp, tuple) or len(resp) > 0:
                return resp
        return [], datetime.now(UTC).replace(microsecond=0)

    async def get_historical_ohlcv_by_start_end(self, coins, interval, start_time, end_time, output_format):
        for provider in self.providers:
            resp = await provider.get_historical_ohlcv_by_start_end(
                coins, interval, start_time, end_time, output_format
            )
            if isinstance(resp, tuple) or len(resp) > 0:
                return resp
        return [], datetime.now(UTC).replace(microsecond=0)

    async def get_historical_ohlcv_by_start_end_for_address(
        self, address, interval, start_time, end_time, output_format
    ):
        for provider in self.providers:
            if isinstance(provider, BirdeyeCoinPriceDataProvider):
                return await provider.get_historical_ohlcv_by_start_end_for_address(
                    address, interval, start_time, end_time, output_format
                )
        print("No birdeye provider found")
        return [], datetime.now(UTC).replace(microsecond=0)

    async def get_historical_ohlcv_for_address(
        self, address, interval, days, output_format
    ):
        for provider in self.providers:
            if isinstance(provider, BirdeyeCoinPriceDataProvider):
                return await provider.get_historical_ohlcv_for_address(
                    address, interval, days, output_format
                )

    async def _get_ca_symbol_birdeye(self, address: str) -> str:
        for provider in self.providers:
            if isinstance(provider, BirdeyeCoinPriceDataProvider):
                return await provider._get_ca_symbol_birdeye(address)
        return address
