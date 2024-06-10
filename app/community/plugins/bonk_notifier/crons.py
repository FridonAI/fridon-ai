import json

from dependency_injector.wiring import Provide

from app.community.plugins.bonk_notifier.helpers.data import read_bonk_summary
from app.community.plugins.bonk_notifier.helpers.llm import (
    generate_bonk_bullish_notification,
    generate_bonk_tag,
)
from app.core.crons import BaseCron
from app.core.crons.registry import ensure_cron_registry
from app.utils.redis.pubsub import Publisher

registry = ensure_cron_registry()


@registry.register
class BonkBullishNotifierCron(BaseCron):
    name = "Bonk Bullish Notifier"
    schedule = "*/1 * * * *"

    async def _process(self, pub: Publisher = Provide["publisher"]) -> None:
        # bonk_summary = await read_bonk_summary()
        # print(bonk_summary)
        # bonk_tag = await generate_bonk_tag(bonk_summary)
        # bonk_notification = await generate_bonk_bullish_notification(bonk_tag)
        # print(bonk_notification)
        await pub.publish(
            "notifications_received",
            # json.dumps({"slug": "bonk-bullish-notifier", "message": bonk_notification}),
            json.dumps(
                {
                    "slug": "bonk-bullish-notifier",
                    "message": "BONK is showing bearish signals. MACD histogram is negative, RSI is below 50, and Stochastic Oscillator is below 20. Chaikin Money Flow indicates money outflow.",
                }
            ),
        )
