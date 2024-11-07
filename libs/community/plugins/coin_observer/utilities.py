from typing import Literal

import pyarrow.compute as pc
from fridonai_core.plugins.utilities.base import BaseUtility

from libs.community.plugins.coin_observer.helpers.llm import get_filter_generator_chain
from libs.community.plugins.coin_observer.schemas import CoinObserverRecord
from libs.repositories.indicators import IndicatorsRepository
from libs.repositories.redis import RedisRepository


class CoinObserverUtility(BaseUtility):
    async def arun(
        self,
        coin_name: str,
        filter: str,
        interval: Literal["1h", "4h", "1d", "1w"] = "1h",
        recurring: bool = False,
        *args,
        wallet_id: str,
        **kwargs,
    ) -> str:
        print(coin_name, interval, filter, wallet_id)
        try:
            filter_expression = await self._generate_filter(coin_name, interval, filter)
        except Exception as e:
            return f"Filter {filter} is not valid"

        await self._save_observer_record(
            wallet_id, coin_name, interval, filter_expression, recurring
        )

        return "Coin observer notification created successfully"

    async def _save_observer_record(
        self,
        wallet_id: str,
        coin_name: str,
        interval: str,
        filter_expression: str,
        recurring: bool,
    ):
        print(wallet_id, coin_name, interval, filter_expression)
        observer_record = CoinObserverRecord(
            coin=coin_name,
            interval=interval,
            filters=filter_expression,
            recurring=recurring,
        )

        coin_observer_repository = RedisRepository(
            table_name="coin_observer_notifications"
        )

        existing_filters = await coin_observer_repository.read(wallet_id)
        if existing_filters is None:
            existing_filters = []

        existing_filters.append(observer_record.model_dump())

        await coin_observer_repository.write(wallet_id, existing_filters)

    async def _generate_filter(
        self, coin_name: str, interval: Literal["1h", "4h", "1d", "1w"], filter: str
    ) -> str:
        filter_generation_chain = get_filter_generator_chain()

        indicators_repository = IndicatorsRepository(
            table_name=f"indicators_{interval}"
        )

        filter_expression = (
            f"({filter_generation_chain.invoke({'schema': indicators_repository.table_schema, 'query': filter}).filters})"
            + f" & (pc.field('coin') == '{coin_name}')"
        )

        print(filter_expression)

        try:
            indicators_repository.get_the_latest_records(eval(filter_expression))
            return filter_expression
        except Exception as e:
            print(e)
            raise ValueError(f"Filter {filter} is not valid")
