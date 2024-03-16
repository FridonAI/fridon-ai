import asyncio

from app.containers import Container
from app.utils import redis

from dependency_injector.wiring import Provide, inject

@inject
async def handler(sub: redis.Subscription = Provide["subscription"]):
    async for message in sub.channel("channel"):
        print(f"(Handler) Message Received: {message}")


if __name__ == "__main__":
    container = Container()
    container.config.redis_host.from_env("REDIS_HOST", "localhost")
    container.config.redis_password.from_env("REDIS_PASSWORD", None)
    container.init_resources()
    container.wire(modules=[__name__])

    loop = asyncio.get_event_loop()
    loop.run_until_complete(handler())