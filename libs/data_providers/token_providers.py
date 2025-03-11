import asyncio
import os
import json
from itertools import groupby
from operator import itemgetter
from pathlib import Path
from datetime import timedelta, datetime, UTC
import aiohttp


class JupiterTokenListDataProvider:
    _instance = None
    _token_list = None
    _cache_dir = Path("../../cache")
    _cache_file = _cache_dir / "token_list_cache.json"
    _cache_duration = timedelta(days=1)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tokens_url = "https://tokens.jup.ag/tokens"
            cls._instance._market_data_url = (
                "https://public-api.birdeye.so/defi/v3/token/market-data"
            )
            cls._instance._birdeye_api_key = os.getenv("BIRDEYE_API_KEY", None)
        return cls._instance

    async def get_token_list(self, tags: list[str] = ["verified"]) -> list[dict]:
        return await self._fetch_token_list(tags)

    async def _fetch_token_list(self, tags: list[str] = ["verified"]) -> list[dict]:
        self._cache_dir.mkdir(exist_ok=True)
        if self._cache_file.exists():
            try:
                with open(self._cache_file, "r") as f:
                    cache_data = json.load(f)
                    cache_time = datetime.fromtimestamp(cache_data["timestamp"], UTC)
                    if datetime.now(UTC) - cache_time < self._cache_duration:
                        return cache_data["token_list"]
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error reading cache file: {e}")
        try:
            async with aiohttp.ClientSession() as session:
                params = {"tags": ",".join(tags)}
                async with session.get(self._tokens_url, params=params) as resp:
                    resp.raise_for_status()
                    initial_token_list = await resp.json()
                    sorted_token_list = sorted(
                        initial_token_list, key=itemgetter("symbol")
                    )

                    token_list = await self._remove_duplicates(sorted_token_list)

                    cache_data = {
                        "timestamp": datetime.now(UTC).timestamp(),
                        "token_list": token_list,
                    }
                    try:
                        with open(self._cache_file, "w") as f:
                            json.dump(cache_data, f)
                    except IOError as e:
                        print(f"Failed to write cache: {e}")

                    return token_list

        except aiohttp.ClientError as e:
            print(f"Failed to fetch token list from API: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error fetching token list: {e}")
            return []


    async def _remove_duplicates(self, sorted_tokens: list[dict]) -> list[dict]:
        # Collect tokens and identify which ones have duplicates
        tokens_by_symbol = {}
        has_duplicates = set()
        print("1")
        for symbol, group in groupby(sorted_tokens, key=itemgetter('symbol')):
            group_tokens = list(group)
            tokens_by_symbol[symbol] = group_tokens
            if len(group_tokens) > 1:
                has_duplicates.add(symbol)

        # For symbols with duplicates, fetch market data
        duplicate_tokens = [token for symbol in has_duplicates for token in tokens_by_symbol[symbol]]
        token_addresses = [token['address'] for token in duplicate_tokens]
        market_data = await self._batch_fetch_token_market_data(token_addresses)

        # Create mapping of address to marketcap
        address_to_marketcap = {address: marketcap for address, marketcap in market_data}

        # Build final token list
        final_token_list = []

        for symbol, tokens in tokens_by_symbol.items():
            if symbol in has_duplicates:
                # For duplicates, keep the one with highest marketcap
                highest_marketcap_token = max(tokens, key=lambda t: address_to_marketcap.get(t['address'], 0))
                final_token_list.append(highest_marketcap_token)
            else:
                # For non-duplicates, keep the single token
                final_token_list.append(tokens[0])

        formated_token_list = [
            {
                "symbol": token["symbol"],
                "address": token["address"],
            }
            for token in final_token_list
        ]

        return formated_token_list

    async def _batch_fetch_token_market_data(
        self, token_list: list[str], batch_size: int = 15
    ) -> list[tuple[str, float]]:
        # Process in batches of 15 tokens per second
        results = []

        for i in range(0, len(token_list), batch_size):
            batch = token_list[i : i + batch_size]
            tasks = [self._fetch_token_market_data(token) for token in batch]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

            if i + batch_size < len(token_list):
                # Wait 1 second before next batch to maintain 15 RPS
                await asyncio.sleep(1)

        return results

    async def _fetch_token_market_data(self, token_address: str) -> tuple[str, float]:
        headers = {
            "accept": "application/json",
            "x-chain": "solana",
            "X-API-KEY": self._birdeye_api_key,
        }
        params = {
            "address": token_address,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self._market_data_url, params=params, headers=headers) as resp:
                data = await resp.json()
                if data["success"] is False:
                    return token_address, 0
                if data["data"] is None:
                    return token_address, 0

                marketcap = data["data"].get("marketcap", 0)
                return token_address, marketcap if marketcap is not None else 0
