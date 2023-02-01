from typing import List, Type
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import func, distinct, select, insert, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.cache import cache
from core.database import Session, get_session
from .models import Menu, Submenu, Dish
from .schemas import BaseSchema


class MenuCRUD:
    def __init__(self, session: Session = Depends(get_session)):
        self.session: AsyncSession = session
        self.model = Menu

    @cache
    async def get_all(self) -> List[Menu]:
        query = await (self.session.execute(
            select(
                Menu.id,
                Menu.title,
                Menu.description,
                func.count(distinct(Submenu.id)).label('submenus_count'),
                func.count(distinct(Dish.id)).label('dishes_count'),
            )
            .outerjoin(Submenu, Menu.id == Submenu.menu_id)
            .outerjoin(Dish, Submenu.id == Dish.submenu_id)
            .group_by(Menu.id)
        ))
        return query.all()

    @cache
    async def get_by_id(self, menu_id: UUID) -> Menu:
        query = (await self.session.execute(
            select(
                Menu.id,
                Menu.title,
                Menu.description,
                func.count(distinct(Submenu.id)).label('submenus_count'),
                func.count(distinct(Dish.id)).label('dishes_count'),
            )
            .outerjoin(Submenu, Menu.id == Submenu.menu_id)
            .outerjoin(Dish, Submenu.id == Dish.submenu_id)
            .filter(Menu.id == menu_id)
            .group_by(Menu.id)
        ))

        item: Menu = query.first()
        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail='menu not found')
        return item

    @cache
    async def create(self, item_data: BaseSchema) -> Menu:
        cursor_result: CursorResult = await self.session.execute(insert(Menu).values(**item_data.dict()))
        await self.session.commit()
        item = self.model(**cursor_result.context.compiled_parameters[0])
        return item

    @cache
    async def update(self, item_id: UUID, item_data: BaseSchema) -> Menu:
        item = await self._get(item_id)
        await self.session.execute(update(self.model).filter_by(id=item_id).values(**item_data.dict()))
        await self.session.commit()
        await self.session.refresh(item)

        return item

    @cache
    async def delete(self, item_id: UUID) -> Menu:
        item = await self._get(item_id)
        await self.session.delete(item)
        await self.session.commit()
        return item

    async def _get(self, item_id: UUID) -> Menu:
        item = await self.session.get(self.model, item_id)
        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail='menu not found')
        return item


class SubmenuCRUD:
    def __init__(self, session: Session = Depends(get_session)):
        self.session: AsyncSession = session
        self.model: Type[Submenu] = Submenu

    @cache
    async def get_all(self, menu_id: UUID) -> List[Submenu]:
        query = (
            await self.session.execute(
                select(
                    Submenu.id,
                    Submenu.title,
                    Submenu.description,
                    func.count(distinct(Dish.id)).label('dishes_count'),
                )
                .outerjoin(Dish, Submenu.id == Dish.submenu_id)
                .filter(Submenu.menu_id == menu_id)
                .group_by(Submenu.id)
            ))
        return query.all()

    @cache
    async def get_by_id(self, submenu_id: UUID, menu_id: UUID) -> Submenu:
        query = (
            await self.session.execute(
                select(
                    Submenu.id,
                    Submenu.title,
                    Submenu.description,
                    func.count(distinct(Dish.id)).label('dishes_count'),
                )
                .outerjoin(Dish, Submenu.id == Dish.submenu_id)
                .filter(Submenu.menu_id == menu_id)
                .filter(Submenu.id == submenu_id)
                .group_by(Submenu.id)
            ))
        item = query.first()
        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail='submenu not found')
        return item

    @cache
    async def create(self, item_data: BaseSchema, menu_id: UUID) -> Submenu:
        cursor_result = await self.session.execute(insert(self.model).values(**item_data.dict(), menu_id=menu_id))
        await self.session.commit()
        item = self.model(**cursor_result.context.compiled_parameters[0])
        return item

    @cache
    async def delete(self, item_id: UUID, menu_id: UUID):
        item = await self._get(item_id, menu_id)
        await self.session.delete(item)
        await self.session.commit()
        return item

    @cache
    async def update(self, item_id: UUID, item_data: BaseSchema, menu_id: UUID) -> Submenu:
        item = await self._get(item_id, menu_id)
        await self.session.execute(update(self.model).filter_by(id=item_id, menu_id=menu_id).values(**item_data.dict()))
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def _get(self, submenu_id: UUID, menu_id: UUID) -> Submenu:
        item = (
            await self.session.scalar(
                select(Submenu)
                .filter(Submenu.id == submenu_id)
                .filter(Menu.id == menu_id)
                .join(Menu, Menu.id == menu_id)
            ))
        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail='submenu not found')
        return item


class DishCRUD:
    def __init__(self, session: Session = Depends(get_session)):
        self.session: AsyncSession = session
        self.model: Type[Dish] = Dish

    @cache
    async def get_all(self, submenu_id: UUID) -> List[Dish]:
        items = await self.session.scalars(select(Dish).filter(Dish.submenu_id == submenu_id))
        return items.all()

    @cache
    async def get_by_id(self, dish_id: UUID, submenu_id: UUID) -> Dish:
        return await self._get(dish_id, submenu_id)

    @cache
    async def create(self, item_data: BaseSchema, submenu_id: UUID, *args, **kwargs) -> Dish:
        cursor_result = await self.session.execute(insert(self.model).values(**item_data.dict(), submenu_id=submenu_id))
        await self.session.commit()
        item = self.model(**cursor_result.context.compiled_parameters[0])
        return item

    @cache
    async def delete(self, item_id: UUID, submenu_id: UUID, *args, **kwargs):
        item = await self._get(item_id, submenu_id)
        await self.session.delete(item)
        await self.session.commit()
        return item

    @cache
    async def update(self, item_id: UUID, item_data: BaseSchema, submenu_id: UUID) -> Dish:
        item = await self._get(item_id, submenu_id)
        await self.session.execute(
            update(self.model).filter_by(id=item_id, submenu_id=submenu_id).values(**item_data.dict()))
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def _get(self, dish_id: UUID, submenu_id: UUID) -> Dish:
        dish: Dish = (
            await self.session.scalar(
                select(Dish)
                .filter(Dish.id == dish_id)
                .filter(Submenu.id == submenu_id)
                .join(Submenu, Submenu.id == submenu_id)
            ))
        if not dish:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail='dish not found')

        return dish
