from dependency_injector import containers, providers
from literalai import LiteralClient

from app import services
from app.settings import settings
from app.utils import redis


class Container(containers.DeclarativeContainer):

    wiring_config = containers.WiringConfiguration(
        modules=[
            "__main__",
            "app.community.plugins.wallet.utilities",
            "app.core.plugins.utilities.blockchain",
            "app.services.process_user_message_service",
            "app.services.calculate_user_message_score_service",
            "app.community.plugins.bonk_notifier.crons",
        ],
        packages=[
            "app.community.plugins",
            "app.core.plugins.utilities",
        ]
    )

    config = providers.Configuration()

    redis_pool = providers.Resource(
        redis.init_redis_pool,
        host=config.redis_host,
        password=config.redis_password,
    )

    subscription = providers.Factory(
        redis.Subscription,
        redis_pool=redis_pool,
    )

    publisher = providers.Factory(
        redis.Publisher,
        redis_pool=redis_pool,
    )

    queue_getter = providers.Factory(
        redis.QueueGetter,
        redis_pool=redis_pool,
    )

    process_user_message_service = providers.Factory(
        services.ProcessUserMessageService,
    )

    calculate_user_message_score_service = providers.Factory(
        services.CalculateUserMessageScoreService,
    )

    literal_client = providers.Factory(
        LiteralClient,
        api_key=settings.LITERAL_API_KEY,
    )

