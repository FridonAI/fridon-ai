from dependency_injector.wiring import Provide
from fridonai_core.crons.base import BaseCron
from fridonai_core.crons.registry import ensure_cron_registry
from fridonai_core.plugins.tools.response_dumper_base import S3ResponseDumper

from libs.utils.redis.pubsub import Publisher
from libs.community.plugins.coin_technical_analyzer.utilities import (
    CoinTechnicalAnalyzerUtility,
)
from libs.community.plugins.coin_technical_chart_searcher.utilities import (
    CoinPriceChartSimilaritySearchUtility,
    CoinPriceChartFalshbackSearchUtility,
)


registry = ensure_cron_registry()


@registry.register
class BonkNotifierCron(BaseCron):
    name: str = "Bonk Notifier"
    schedule: str = "*/1 * * * *"

    async def _process(self, pub: Publisher = Provide["publisher"]) -> None:
        coin_technical_analyzer_utility = CoinTechnicalAnalyzerUtility()
        bonk_analysis = await coin_technical_analyzer_utility.arun(
            coin_name="BONK",
            interval="1h",
        )
        coin_price_chart_similarity_search_utility = (
            CoinPriceChartSimilaritySearchUtility()
        )

        similar_coins = await coin_price_chart_similarity_search_utility.arun(
            coin_name="BONK",
            interval="1h",
        )
        coin_price_chart_falshback_search_utility = (
            CoinPriceChartFalshbackSearchUtility()
        )
        flashback_coins = await coin_price_chart_falshback_search_utility.arun(
            coin_name="BONK",
            interval="1h",
        )

        response_dumper = S3ResponseDumper()

        result = (
            await response_dumper.dump(
                {
                    "coin_analysis": bonk_analysis,
                    "similar_coins": similar_coins,
                    "flashback_coins": flashback_coins,
                },
                "bonk_notifier",
            )
        ).model_dump_json()

        print(result)

        await pub.publish("bonk_notifier", result)
