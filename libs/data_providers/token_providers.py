import asyncio
import os
from itertools import groupby
from operator import itemgetter

import aiohttp


class JupiterTokenListDataProvider:
    _instance = None
    _token_list = None

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
        if self._token_list is None:
            initial_token_list = await self._fetch_token_list(tags)
            sorted_token_list = sorted(initial_token_list, key=itemgetter('symbol'))
            self._token_list = await self._remove_duplicates(sorted_token_list)
        return self._token_list


    async def _fetch_token_list(self, tags: list[str] = ["verified"]) -> list[dict]:
        try:
            async with aiohttp.ClientSession() as session:
                params = {"tags": ",".join(tags)}
                async with session.get(f"{self._tokens_url}", params=params) as resp:
                    return await resp.json()
        except Exception as e:
            print(f"Failed to fetch token list: {e}")
            return []

    async def _remove_duplicates(self, sorted_tokens: list[dict]) -> list[dict]:
        # Collect tokens and identify which ones have duplicates
        tokens_by_symbol = {}
        has_duplicates = set()

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
