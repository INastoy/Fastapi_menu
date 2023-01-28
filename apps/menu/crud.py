from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import func, distinct
from starlette import status

from core.cache import cache
from core.database import Session, get_session
from .models import Menu, Submenu, Dish
from .schemas import BaseSchema


class MenuCRUD:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session
        self.model = Menu

    def get_all(self) -> List[Menu]:
        return (
            self.session.query(
                Menu.id,
                Menu.title,
                Menu.description,
                func.count(distinct(Submenu.id)).label('submenus_count'),
                func.count(distinct(Dish.id)).label('dishes_count'),
            )
            .outerjoin(Submenu, Menu.id == Submenu.menu_id)
            .outerjoin(Dish, Submenu.id == Dish.submenu_id)
            .group_by(Menu.id)
            .all()
        )

    @cache
    def get_by_id(self, menu_id: UUID) -> Menu:
        item = (
            self.session.query(
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
            .first()
        )
        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail='menu not found')
        return item

    @cache
    def create(self, item_data: BaseSchema) -> Menu:
        item = self.model(**item_data.dict())
        self.session.add(item)
        self.session.commit()
        return item

    @cache
    def update(self, item_id: UUID, item_data: BaseSchema) -> Menu:
        item = self._get(item_id)
        for field, value in item_data:
            setattr(item, field, value)
        self.session.commit()
        return item

    @cache
    def delete(self, item_id: UUID) -> Menu:
        item = self._get(item_id)
        self.session.delete(item)
        self.session.commit()
        return item

    def _get(self, item_id: UUID) -> Menu:
        item = self.session.query(self.model).filter(
            self.model.id == item_id).first()
        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail='menu not found')
        return item


class SubmenuCRUD:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session
        self.model = Submenu

    @cache
    def get_all(self, menu_id: UUID) -> List[Submenu]:
        return (
            self.session.query(
                Submenu.id,
                Submenu.title,
                Submenu.description,
                func.count(distinct(Dish.id)).label('dishes_count'),
            )
            .outerjoin(Dish, Submenu.id == Dish.submenu_id)
            .filter(Submenu.menu_id == menu_id)
            .group_by(Submenu.id)
            .all()
        )

    @cache
    def get_by_id(self, submenu_id: UUID, menu_id: UUID) -> Submenu:
        item = (
            self.session.query(
                Submenu.id,
                Submenu.title,
                Submenu.description,
                func.count(distinct(Dish.id)).label('dishes_count'),
            )
            .outerjoin(Dish, Submenu.id == Dish.submenu_id)
            .filter(Submenu.menu_id == menu_id)
            .filter(Submenu.id == submenu_id)
            .group_by(Submenu.id)
            .first()
        )
        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail='submenu not found')
        return item

    @cache
    def create(self, item_data: BaseSchema, menu_id: UUID) -> Submenu:
        item = self.model(**item_data.dict(), menu_id=menu_id)
        self.session.add(item)
        self.session.commit()
        return item

    @cache
    def delete(self, item_id: UUID, menu_id: UUID):
        item = self._get(item_id, menu_id)
        self.session.delete(item)
        self.session.commit()
        return item

    @cache
    def update(self, item_id: UUID, item_data: BaseSchema, menu_id: UUID) -> Submenu:
        item = self._get(item_id, menu_id)
        for field, value in item_data:
            setattr(item, field, value)
        self.session.commit()
        return item

    def _get(self, submenu_id: UUID, menu_id: UUID) -> Submenu:
        menu = (
            self.session.query(Submenu)
                .filter(Submenu.id == submenu_id)
                .filter(Menu.id == menu_id)
                .join(Menu, Menu.id == menu_id)
                .first()
        )
        if not menu:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail='submenu not found')
        return menu


class DishCRUD:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session
        self.model = Dish

    @cache
    def get_all(self, submenu_id: UUID) -> List[Dish]:
        return self.session.query(Dish).filter(Dish.submenu_id == submenu_id).all()

    @cache
    def get_by_id(self, dish_id: UUID, submenu_id: UUID) -> Dish:
        return self._get(dish_id, submenu_id)

    @cache
    def create(self, item_data: BaseSchema, submenu_id: UUID, *args, **kwargs) -> Dish:
        item = self.model(**item_data.dict(), submenu_id=submenu_id)
        self.session.add(item)
        self.session.commit()
        return item

    @cache
    def delete(self, item_id: UUID, submenu_id: UUID, *args, **kwargs):
        item = self._get(item_id, submenu_id)
        self.session.delete(item)
        self.session.commit()
        return item

    @cache
    def update(self, item_id: UUID, item_data: BaseSchema, submenu_id: UUID) -> Dish:
        item = self._get(item_id, submenu_id)
        for field, value in item_data:
            setattr(item, field, value)
        self.session.commit()
        return item

    def _get(self, dish_id: UUID, submenu_id: UUID) -> Dish:
        dish: Dish = (
            self.session.query(Dish)
                .filter(Dish.id == dish_id)
                .filter(Submenu.id == submenu_id)
                .join(Submenu, Submenu.id == submenu_id)
                .first()
        )
        if not dish:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail='dish not found')
        return dish
