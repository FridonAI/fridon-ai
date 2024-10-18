import json
from datetime import datetime, timedelta
from typing import Literal
import pyarrow.compute as pc


import requests

from fridonai_core.plugins.utilities import BaseUtility
from libs.community.plugins.coin_technical_analyzer.helpers.llm import get_filter_generator_chain
from libs.repositories.indicators import IndicatorsRepository
from settings import settings


class CoinPriceChartSimilaritySearchUtility(BaseUtility):
    async def arun(
        self, coin_name: str, start_date: str | None = None, *args, **kwargs
    ) -> str | dict:
        if start_date is not None:
            start_date = datetime.fromisoformat(start_date)
            end_date = min(start_date + timedelta(days=30), datetime.now())
        else:
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()

        req = {
            "coin": coin_name.upper(),
            "from": int(start_date.timestamp() * 1000),
            "to": int(end_date.timestamp() * 1000),
            "topK": 3,
        }

        resp = requests.post(
            settings.API_URL + "/blockchain/coin-similarity", json=req
        ).json()

        if "statusCode" in resp:
            if 500 > resp["statusCode"] >= 400:
                return resp.get("message", "Something went wrong!")
            if resp["statusCode"] >= 500:
                return "Something went wrong! Please try again later."

        return  {
            "type": "similar_coins",
            "coin": coin_name,
            "start_date_timestamp": int(start_date.timestamp()),
            "end_date_timestamp": int(end_date.timestamp()),
            "start_date": start_date.strftime("%d %B %Y"),
            "end_date": end_date.strftime("%d %B %Y"),
            **resp,
        }
    

class CoinTechnicalIndicatorsSearchUtility(BaseUtility):
    async def arun(
        self, filter: str, interval: Literal["1h", "4h", "1d", "1w"] = "4h", *args, **kwargs
    ) -> list[dict]:
        filter_generation_chain = get_filter_generator_chain()

        indicators_repository = IndicatorsRepository(
            table_name=f"indicators_{interval}"
        )

        filter_expression = filter_generation_chain.invoke(
            {"schema": indicators_repository.table_schema, "query": filter}
        ).filters

        print("Filter expression: ", filter_expression)

        latest_records = indicators_repository.get_the_latest_records(
            eval(filter_expression)
        )

        if len(latest_records) == 0:
            return "No coins found"

        return latest_records.to_dicts()