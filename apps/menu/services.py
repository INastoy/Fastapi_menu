import traceback
from typing import Optional, Union
from uuid import UUID

from fastapi import Depends
from starlette.responses import FileResponse

from apps.menu.crud import DishCRUD, MenuCRUD, SubmenuCRUD
from apps.menu.models import Dish, Menu, Submenu
from apps.menu.schemas import BaseSchema
from core.cache.redis import RedisCache


class MenuService:

    def __init__(self, repository: MenuCRUD = Depends(), cache: RedisCache = Depends()):
        self.repository = repository
        self.cache = cache
        self.cache_for_invalidate = ['MenuService.get_all']

    async def get_all(self) -> list[Menu]:
        key = await self._get_cache_key()
        cached_data = await self.cache.get(key)
        if not cached_data:
            db_data = await self.repository.get_all()
            await self.cache.set(key, db_data)

            return db_data
        return cached_data

    async def get_by_id(self, item_id: UUID) -> Menu:
        key = await self._get_cache_key(item_id)
        cached_data = await self.cache.get(key)
        if not cached_data:
            db_data = await self.repository.get_by_id(item_id)
            await self.cache.set(key, db_data)

            return db_data
        return cached_data

    async def create(self, item_data: BaseSchema) -> Menu:
        item = await self.repository.create(item_data)
        await self.cache.bulk_delete(self.cache_for_invalidate)
        return item

    async def delete(self, item_id: UUID) -> Menu:
        key = await self._get_cache_key(item_id)
        item = await self.repository.delete(item_id)
        await self._del_invalid_cache(key)
        return item

    async def update(self, item_id: UUID, item_data: BaseSchema) -> Menu:
        key = await self._get_cache_key(item_id)
        item = await self.repository.update(item_id, item_data)
        await self._del_invalid_cache(key)

        return item

    async def _get_cache_key(self, item_id: Optional[UUID] = None) -> str:
        class_name = self.__class__.__name__
        if item_id is None:
            func_name = traceback.extract_stack()[-2].name
            return f'{class_name}.{func_name}'
        key = f'{class_name}.{item_id}'
        return key

    async def _get_invalid_cache(self, key: Union[str, UUID]) -> list[Union[str, UUID]]:
        invalid_cache = [*self.cache_for_invalidate, key]

        return invalid_cache

    async def _del_invalid_cache(self, key: str) -> None:
        invalid_cache = await self._get_invalid_cache(key)
        await self.cache.bulk_delete(invalid_cache)

    async def create_example(self, file_path: str) -> dict:
        return await self.repository.create_example(file_path)

    async def generate_excel(self) -> dict:
        return await self.repository.generate_excel()

    async def get_excel(self, file_id: UUID) -> FileResponse:
        return await self.repository.get_excel(file_id)


class SubmenuService:

    def __init__(self, repository: SubmenuCRUD = Depends(), cache: RedisCache = Depends()):
        self.repository: SubmenuCRUD = repository
        self.cache: RedisCache = cache
        self.cache_for_invalidate = ('MenuService.get_all', )

    async def get_all(self, menu_id: UUID) -> list[Submenu]:
        key = await self._get_cache_key(menu_id)
        cached_data = await self.cache.get(key)
        if not cached_data:
            db_data = await self.repository.get_all(menu_id)
            await self.cache.set(key, db_data)

            return db_data
        return cached_data

    async def get_by_id(self, item_id: UUID, menu_id: UUID) -> Submenu:
        key = await self._get_cache_key(item_id)
        cached_data = await self.cache.get(key)
        if not cached_data:
            db_data = await self.repository.get_by_id(item_id, menu_id)
            await self.cache.set(key, db_data)

            return db_data
        return cached_data

    async def create(self, item_data: BaseSchema, menu_id: UUID) -> Submenu:
        key = await self._get_cache_key(menu_id)
        item = await self.repository.create(item_data, menu_id)
        await self._del_invalid_cache(key, menu_id)
        return item

    async def delete(self, item_id: UUID, menu_id: UUID) -> Submenu:
        key = await self._get_cache_key(item_id)
        item = await self.repository.delete(item_id, menu_id)
        await self._del_invalid_cache(key, menu_id)
        return item

    async def update(self, item_id: UUID, item_data: BaseSchema, menu_id: UUID) -> Submenu:
        key = await self._get_cache_key(item_id)
        item = await self.repository.update(item_id, item_data, menu_id)
        await self._del_invalid_cache(key, menu_id)

        return item

    async def _get_cache_key(self, item_id: Optional[UUID] = None) -> str:
        class_name = self.__class__.__name__
        key = f'{class_name}.{item_id}'
        return key

    async def _get_invalid_cache(self, key: Union[str, UUID], menu_id: UUID) -> list[Union[str, UUID]]:
        menu = f'{MenuService().__class__.__qualname__}.{menu_id}'
        menu_submenus = await self._get_cache_key(menu_id)
        invalid_cache = [menu, menu_submenus, key, *self.cache_for_invalidate]

        return invalid_cache

    async def _del_invalid_cache(self, key: str, menu_id: UUID) -> None:
        invalid_cache = await self._get_invalid_cache(key, menu_id)
        await self.cache.bulk_delete(invalid_cache)


class DishService:

    def __init__(self, repository: DishCRUD = Depends(), cache: RedisCache = Depends()):
        self.repository: DishCRUD = repository
        self.cache: RedisCache = cache
        self.cache_for_invalidate = ('MenuService.get_all',)

    async def get_all(self, submenu_id: UUID) -> list[Dish]:
        key = await self._get_cache_key(submenu_id)
        cached_data = await self.cache.get(key)
        if not cached_data:
            db_data = await self.repository.get_all(submenu_id)
            await self.cache.set(key, db_data)

            return db_data
        return cached_data

    async def get_by_id(self, item_id: UUID, submenu_id: UUID) -> Dish:
        key = await self._get_cache_key(item_id)
        cached_data = await self.cache.get(key)
        if not cached_data:
            db_data = await self.repository.get_by_id(item_id, submenu_id)
            await self.cache.set(key, db_data)

            return db_data
        return cached_data

    async def create(self, item_data: BaseSchema, submenu_id: UUID, menu_id: UUID) -> Dish:
        key = await self._get_cache_key()
        item = await self.repository.create(item_data, submenu_id, menu_id)
        await self._del_invalid_cache(key, submenu_id, menu_id)
        return item

    async def delete(self, item_id: UUID, submenu_id: UUID, menu_id: UUID) -> Dish:
        key = await self._get_cache_key(item_id)
        item = await self.repository.delete(item_id, submenu_id, menu_id)
        await self._del_invalid_cache(key, submenu_id, menu_id)

        return item

    async def update(self, item_id: UUID, item_data: BaseSchema, submenu_id: UUID, menu_id: UUID) -> Dish:
        key = await self._get_cache_key(item_id)
        item = await self.repository.update(item_id, item_data, submenu_id)
        await self._del_invalid_cache(key, submenu_id, menu_id)

        return item

    async def _get_cache_key(self, item_id: Optional[UUID] = None) -> str:
        class_name = self.__class__.__name__
        key = f'{class_name}.{item_id}'
        return key

    async def _get_invalid_cache(self, key: Union[str, UUID], submenu_id: UUID, menu_id: UUID) -> list[Union[str, UUID]]:
        menu = f'{MenuService().__class__.__name__}.{menu_id}'
        submenu = f'{SubmenuService().__class__.__name__}.{submenu_id}'
        submenu_dishes = await self._get_cache_key(submenu_id)
        invalid_cache = [menu, submenu, submenu_dishes,
                         key, *self.cache_for_invalidate]

        return invalid_cache

    async def _del_invalid_cache(self, key: str, submenu_id: UUID, menu_id: UUID) -> None:
        invalid_cache = await self._get_invalid_cache(key, submenu_id, menu_id)
        await self.cache.bulk_delete(invalid_cache)
