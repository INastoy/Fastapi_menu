import json
from typing import Any, Union
from uuid import UUID

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from redis.asyncio.client import Redis  # type: ignore
from redis.asyncio.connection import ConnectionPool  # type: ignore
from starlette.background import BackgroundTasks

from core.settings import CACHE_EXPIRATION, CACHE_URL


async def get_cache_client() -> Redis:
    connection_pool = ConnectionPool.from_url(url=CACHE_URL)
    async_cache_client = Redis(connection_pool=connection_pool)
    async with async_cache_client as cache_client:
        yield cache_client


class RedisCache:

    def __init__(self, bg_tasks: BackgroundTasks, cache_client: Redis = Depends(get_cache_client)):
        self.client = cache_client
        self.background_tasks = bg_tasks

    async def get(self, key: Union[UUID, str]):
        cached_data = await self.client.get(key)
        return json.loads(cached_data) if cached_data else None

    async def set(
            self,
            key: Union[UUID, str],
            value: Any,
            *args,
            as_task: bool = True,
            ex: int = CACHE_EXPIRATION,
            **kwargs):
        json_value = json.dumps(jsonable_encoder(value))
        if as_task:
            self.background_tasks.add_task(
                self.client.set, key, json_value, ex, *args, **kwargs)
            # fix bug with wrong detection async func by BackgroundTasks
            self.background_tasks.tasks[0].is_async = True
        else:
            await self.client.set(key, json_value, ex, *args, **kwargs)

    async def delete(self, key: Union[UUID, str], as_task: bool = True):
        if as_task:
            self.background_tasks.add_task(self.client.delete, key)
            # fix bug with wrong detection async func by BackgroundTasks
            self.background_tasks.tasks[0].is_async = True
        else:
            await self.client.delete(key)

    async def bulk_delete(self, keys: list, as_task: bool = True):
        if as_task:
            self.background_tasks.add_task(self.client.delete, *keys)
            # fix bug with wrong detection async func by BackgroundTasks
            self.background_tasks.tasks[0].is_async = True
        else:
            await self.client.delete(*keys)
