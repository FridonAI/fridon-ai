import json
from typing import Any, AsyncIterator
from pydantic import ConfigDict, Field, BaseModel
from redis.asyncio import Redis
from libs.utils.redis.pool import init_redis_pool
from settings import settings


class RedisRepository(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    table_name: str = Field(...)
    redis: Redis = None

    async def initialize(self):
        if self.redis is None:
            host = settings.REDIS_HOST
            password = None  # TODO change to settings.REDIS_PASSWORD
            self.redis = await anext(init_redis_pool(host=host, password=password))

    async def read(self, key: str) -> Any:
        await self.initialize()
        json_str = await self.redis.hget(self.table_name, key)
        if json_str is None:
            return None
        return json.loads(json_str)

    async def all(self) -> list[Any]:
        await self.initialize()
        all_records = await self.redis.hgetall(self.table_name)
        return [
            (key, json.loads(value)) for key, value in all_records.items()
        ]

    async def write(self, key: str, value: Any) -> None:
        await self.initialize()
        await self.redis.hset(self.table_name, key, json.dumps(value))
