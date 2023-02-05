import redis.asyncio as redis  # type: ignore

from core.settings import CACHE_URL

connection_pool = redis.ConnectionPool.from_url(url=CACHE_URL)  # type: ignore
cache_client = redis.StrictRedis(
    connection_pool=connection_pool)  # type: ignore
