import json
from datetime import datetime, timedelta

import requests

from app.core.plugins.utilities import BaseUtility
from app.settings import settings


class CoinPriceChartSimilaritySearchUtility(BaseUtility):
    async def arun(
            self,
            coin_name: str,
            start_date: str | None = None,
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
            "coin": coin_name,
            "from": int(start_date.timestamp()),
            "to": int(end_date.timestamp()),
            "topK": 3
        }

        resp = requests.post(settings.API_URL + '/blockchain/coin-similarity', json=req).json()

        if "statusCode" in resp:
            if 500 > resp["statusCode"] >= 400:
                return resp.get("message", "Something went wrong!")
            if resp["statusCode"] >= 500:
                return "Something went wrong! Please try again later."

        return json.dumps({
            "type": "similar_coins",
            "coin": coin_name,
            "start_date_timestamp": int(start_date.timestamp()),
            "end_date_timestamp": int(end_date.timestamp()),
            "start_date": start_date.strftime("%d %B %Y"),
            "end_date": end_date.strftime("%d %B %Y"),
            **resp,
        })
