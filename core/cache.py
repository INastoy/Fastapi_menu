import pickle
from typing import Generator, Callable
from uuid import UUID

from core.redis import cache_client
from core.settings import CACHE_EXPIRATION


def _get_uuid(*args, **kwargs):
    params = list(args)
    params.extend(kwargs.values())
    for i in params:
        if isinstance(i, UUID):
            yield str(i)


def _delete_cache(items_uuid: Generator):
    cache_client.delete('MenuCRUD.get_all',
                        'SubmenuCRUD.get_all', 'DishCRUD.get_all')
    for item_uuid in items_uuid:
        cache_client.delete(item_uuid)


def cache(function: Callable):
    def wrapper(self, *args, **kwargs):
        items_uuid = _get_uuid(*args, **kwargs)
        if function.__name__ in ('create', 'update', 'delete'):
            db_data = function(self, *args, **kwargs)
            _delete_cache(items_uuid)

            return db_data

        redis_key = (function.__qualname__
                     if function.__name__ == 'get_all'
                     else next(items_uuid))

        cached_data = cache_client.get(redis_key)
        if not cached_data:
            db_data = function(self, *args, **kwargs)
            cache_client.set(redis_key, pickle.dumps(
                db_data), ex=CACHE_EXPIRATION)

            return db_data
        return pickle.loads(cached_data)

    return wrapper