from collections.abc import AsyncIterator

from redis.asyncio import Redis

import json

from app.schema import Request

STOPWORD = "STOP"


class Subscription:
    def __init__(self, redis_pool: Redis) -> None:
        self.redis_pool = redis_pool

    async def channel(self, channel_name: str) -> AsyncIterator[Request]:
        async with self.redis_pool.pubsub() as pubsub:
            await pubsub.subscribe(channel_name)
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    if message["data"] == STOPWORD:
                        print("(Reader) STOP")
                        break
                    yield Request.parse_obj(json.loads(message["data"])["data"])
            await pubsub.unsubscribe(channel_name)


class Publisher:
    def __init__(self, redis_pool: Redis) -> None:
        self.redis_pool = redis_pool

    async def publish(self, channel_name: str, message: str) -> None:
        print("Publishing message", message)
        await self.redis_pool.publish(channel_name, message)


class QueueGetter:
    def __init__(self, redis_pool: Redis) -> None:
        self.redis_pool = redis_pool

    async def get(self, queue_name: str) -> str:
        message = await self.redis_pool.blpop([queue_name], timeout=60)
        if message is None or len(message) == 0:
            return "Something wrong happened!"
        # print('Got message 2', message)
        return json.loads(message[1]).get("data", "Something wrong happened!")

