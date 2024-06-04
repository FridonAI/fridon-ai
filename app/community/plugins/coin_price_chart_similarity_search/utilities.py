import json
import os
from datetime import datetime, timedelta

import requests

from app.core.plugins.utilities import BaseUtility


class CoinPriceChartSimilaritySearchUtility(BaseUtility):
    name = "coin-price-chart-similarity-search"
    description = "A utility that allows you to search for similar coins by price chart of the given time range"

    async def run(
            self,
            coin: str,
            start_date: str,
            *args,
            **kwargs
    ) -> str:
        if start_date is not None:
            start_date = datetime.fromisoformat(start_date)
            end_date = min(start_date + timedelta(days=30), datetime.now())
        else:
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()

        req = {
            "coin": coin,
            "from": int(start_date.timestamp()),
            "to": int(end_date.timestamp()),
            "topK": 3
        }

        print("Request", req)

        api_url = os.environ["API_URL"]
        if not api_url:
            raise Exception("API_URL not set in environment variables")

        resp = requests.post(api_url + '/executor', json=req).json()

        if "statusCode" in resp:
            if 500 > resp["statusCode"] >= 400:
                return resp.get("message", "Something went wrong!")
            if resp["statusCode"] >= 500:
                return "Something went wrong! Please try again later."

        print("Response", resp)
        return json.dumps({
            "type": "similar_coins",
            "coin": coin,
            "start_date_timestamp": int(start_date.timestamp()),
            "end_date_timestamp": int(end_date.timestamp()),
            "start_date": start_date.strftime("%d %B %Y"),
            "end_date": end_date.strftime("%d %B %Y"),
            **resp,
        })

