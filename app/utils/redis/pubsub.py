import asyncio
from typing import AsyncIterator

import async_timeout

from redis.asyncio import Redis
from redis.asyncio.client import PubSub

STOPWORD = "STOP"

class Subscription(object):
    def __init__(self, redis_pool: Redis) -> None:
        self.redis_pool = redis_pool

    async def channel(self, channel_name: str) -> AsyncIterator[str]:
        async with self.redis_pool.pubsub() as pubsub:
            await pubsub.subscribe(channel_name)
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    print(f"(Reader) Message Received: {message}")
                    if message["data"] == STOPWORD:
                        print("(Reader) STOP")
                        break
                    yield message["data"]
            await pubsub.unsubscribe(channel_name)

class Publisher(object):
    def __init__(self, redis_pool: Redis) -> None:
        self.redis_pool = redis_pool

    async def publish(self, channel_name: str, message: str) -> None:
        await self.redis_pool.publish(channel_name, message)

