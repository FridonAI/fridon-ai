from collections.abc import AsyncIterator

from redis.asyncio import ConnectionPool, Redis


async def init_redis_pool(host: str, password: str) -> AsyncIterator[Redis]:
    pool = ConnectionPool.from_url(f"redis://{host}", password=password, encoding="utf-8", decode_responses=True)
    redis = Redis.from_pool(pool)
    try:
        yield redis
    finally:
        await redis.close()
