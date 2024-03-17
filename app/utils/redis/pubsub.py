from collections.abc import AsyncIterator

from redis.asyncio import Redis

import json

STOPWORD = "STOP"

class Subscription:
    def __init__(self, redis_pool: Redis) -> None:
        self.redis_pool = redis_pool

    async def channel(self, channel_name: str) -> AsyncIterator[dict]:
        async with self.redis_pool.pubsub() as pubsub:
            await pubsub.subscribe(channel_name)
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    if message["data"] == STOPWORD:
                        print("(Reader) STOP")
                        break
                    yield json.loads(message["data"])
            await pubsub.unsubscribe(channel_name)

class Publisher:
    def __init__(self, redis_pool: Redis) -> None:
        self.redis_pool = redis_pool

    async def publish(self, channel_name: str, message: str) -> None:
        await self.redis_pool.publish(channel_name, message)

