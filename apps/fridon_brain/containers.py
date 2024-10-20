from dependency_injector import containers, providers
from literalai import LiteralClient

from apps.fridon_brain import services
from libs.utils import redis
from settings import settings


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "__main__",
            "libs.community.plugins.wallet.utilities",
            "apps.fridon_brain.services.process_user_message_service",
            "apps.fridon_brain.services.calculate_user_message_score_service",
        ],
        packages=[
            "libs.community.plugins",
        ],
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
