import requests


class BirdEyeApiClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    def get(self, path: str, params: dict, **kwargs) -> dict:
        response = requests.get(f"{self.base_url}/{path}", headers={"X-API-KEY": self.api_key},
                                params=params)

        response.raise_for_status()

        return response.json()

    def get_history(self, coin_address: str, time_from: int, time_to: int, interval: str = "1H") -> list[dict]:
        response = self.get("history_price",
                            {"address": coin_address, "time_from": time_from, "time_to": time_to, "type": interval})

        if response["success"] and response["data"]["items"]:
            return response["data"]["items"]
        else:
            raise ValueError(f"Failed to fetch history for {coin_address}")
