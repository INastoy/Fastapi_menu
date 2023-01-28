import redis

from core.settings import CACHE_URL

# redis_client = redis.Redis(decode_responses=True)

connection_pool = redis.ConnectionPool.from_url(url=CACHE_URL)  # type: ignore
cache_client = \
    redis.StrictRedis(connection_pool=connection_pool)  # type: ignore
