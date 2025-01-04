import json
import pyarrow.compute as pc
from dependency_injector.wiring import Provide
from fridonai_core.crons import BaseCron
from fridonai_core.crons.registry import ensure_cron_registry

from libs.community.plugins.coin_observer.schemas import CoinObserverRecord
from libs.repositories.indicators import IndicatorsRepository
from libs.repositories.redis import RedisRepository
from libs.utils.redis.pubsub import Publisher
from libs.community.plugins.coin_observer.helpers.llm import get_response_generator_chain

registry = ensure_cron_registry()


@registry.register
class CoinObserverCron(BaseCron):
    name: str = "Coin Observer"
    schedule: str = "*/20 * * * *"

    async def _process(self, pub: Publisher = Provide["publisher"]) -> None:
        coin_observer_repository = RedisRepository(
            table_name="coin_observer_notifications"
        )
        all_coin_observer_records_raw = await coin_observer_repository.all()
        grouped_filters = [
            {"wallet_id": key, "filters": [CoinObserverRecord(**r) for r in value]}
            for key, value in all_coin_observer_records_raw
        ]
        grouped_filters
        # for record in grouped_filters:
        #     wallet_id = record["wallet_id"]
        #     filters = record["filters"]

        #     for filter in filters:
        #         interval = filter.interval
        #         filter_expression = filter.filters
        #         indicators_repository = IndicatorsRepository(
        #             table_name=f"indicators_{interval}"
        #         )
        #         latest_records = indicators_repository.get_the_latest_records(
        #             eval(filter_expression)
        #         )
        #         if len(latest_records) != 0:
        #             chain = get_response_generator_chain()
        #             response = await chain.ainvoke(
        #                 {
        #                     "coin": latest_records[0]["coin"],
        #                     "filter": filter.filters,
        #                     "indicators": latest_records.to_dicts(),
        #                 }
        #             )

        #             await pub.publish(
        #                 "notifications_received",
        #                 json.dumps(
        #                     {
        #                         "walletId": wallet_id,
        #                         "slug": "coin-observer",
        #                         "message": response,
        #                     }
        #                 ),
        #             )

        #             if not filter.recurring:
        #                 existing_filters = await coin_observer_repository.read(wallet_id)
        #                 existing_filters = [x for x in existing_filters if x["id"] != filter.id]
        #                 await coin_observer_repository.write(wallet_id, existing_filters)
