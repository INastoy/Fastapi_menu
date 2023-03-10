# import pickle
# from typing import Callable, Generator
# from uuid import UUID
#
# from core.cache.redis import cache_client
# from core.settings import CACHE_EXPIRATION
#
#
# def _get_uuid(*args, **kwargs) -> Generator:
#     params = list(args)
#     params.extend(kwargs.values())
#     for i in params:
#         if isinstance(i, UUID):
#             yield str(i)
#
#
# async def _delete_cache(items_uuid: Generator):
#     keys_to_delete = ['MenuCRUD.get_all',
#                       'SubmenuCRUD.get_all', 'DishCRUD.get_all']
#     uuids_to_delete = list(items_uuid)
#     keys_to_delete.extend(uuids_to_delete)
#     await cache_client.delete(*keys_to_delete)
#
#
# def cache(function: Callable):
#     async def wrapper(self, *args, **kwargs):
#         items_uuid = _get_uuid(*args, **kwargs)
#         if function.__name__ in ('create', 'create_example', 'update', 'delete'):
#             db_data = await function(self, *args, **kwargs)
#             await _delete_cache(items_uuid)
#
#             return db_data
#
#         redis_key = function.__qualname__ if function.__name__ == 'get_all' else next(
#             items_uuid)
#
#         cached_data = await cache_client.get(redis_key)
#         if not cached_data:
#             db_data = await function(self, *args, **kwargs)
#             await cache_client.set(redis_key, pickle.dumps(db_data), ex=CACHE_EXPIRATION)
#
#             return db_data
#         return pickle.loads(cached_data)
#
#     return wrapper
