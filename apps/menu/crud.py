import uuid
from typing import Type, List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import func, distinct
from starlette import status

from services.database import Session, get_session
from .models import Menu, Submenu, Dish, Base
from .schemas import BaseSchema


class AbstractCRUD:
    def __init__(self, session: Session = Depends(get_session), model: Type[Base] = None):
        self.session = session
        self.model = model

    def get_all(self) -> List[Type[Base]]:
        return self.session.query(self.model).all()

    def get_by_id(self, item_id: str) -> Type[Base]:
        return self._get(item_id)

    def create(self, item_data: BaseSchema) -> Type[Base]:
        item = self.model(**item_data.dict())
        self.session.add(item)
        self.session.commit()
        return item

    def update(self, item_id: str, item_data: BaseSchema, ) -> Type[Base]:
        item = self._get(item_id)
        for field, value in item_data:
            setattr(item, field, value)
        self.session.commit()
        return item

    def delete(self, item_id: str, ):
        item = self._get(item_id)
        self.session.delete(item)
        self.session.commit()

    def _get(self, item_id: str) -> Optional[Type[Base]]:
        if len(item_id) != 36:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        item = self.session.query(self.model).filter(self.model.id == item_id).one_or_none()
        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        return item


class MenuCRUD(AbstractCRUD):
    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session)
        self.model = Menu

    def get_all(self) -> List[Menu]:
        return self.session.query(
            Menu.id,
            Menu.title,
            Menu.description,
            func.count(distinct(Submenu.id)).label('submenus_count'),
            func.count(distinct(Dish.id)).label('dishes_count'))\
            .outerjoin(Submenu, Menu.id == Submenu.menu_id)\
            .outerjoin(Dish, Submenu.id == Dish.submenu_id)\
            .group_by(Menu.id)\
            .all()
        # return self.session.query(Menu).group_by(Menu.id).all()
    #
    # def get_by_id(self, menu_id: int) -> Menu:
    #     menu = self._get(menu_id)
    #     return menu
    #
    # def create(self, menu_data: MenuSchema) -> Menu:
    #     menu = Menu(**menu_data.dict())
    #     self.session.add(menu)
    #     self.session.commit()
    #     return menu
    #
    # def update(self, menu_id: int, menu_data: MenuSchema, ) -> Menu:
    #     menu = self._get(menu_id)
    #     for field, value in menu_data:
    #         setattr(menu, field, value)
    #     self.session.commit()
    #     return menu
    #
    # def delete(self, menu_id: int, ):
    #     menu = self._get(menu_id)
    #     self.session.delete(menu)
    #     self.session.commit()
    #
    # def _get(self, menu_id: int) -> Optional[Menu]:
    #     menu = self.session.query(Menu).filter(Menu.id == menu_id).first()
    #     if not menu:
    #         raise HTTPException(status.HTTP_404_NOT_FOUND)
    #     return menu


class SubmenuCRUD(AbstractCRUD):

    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session)
        self.model = Submenu

    def get_all(self) -> List[Submenu]:
        return self.session.query(
            Submenu.id,
            Submenu.title,
            Submenu.description,
            func.count(distinct(Dish.id)).label('dishes_count'))\
            .outerjoin(Dish, Submenu.id == Dish.submenu_id)\
            .group_by(Submenu.id)\
            .all()
    #
    # def get_by_id(self, menu_id: int) -> Submenu:
    #     menu = self._get(menu_id)
    #     return menu
    #
    # def create(self, menu_data: SubmenuSchema) -> Submenu:
    #     menu = Submenu(**menu_data.dict())
    #     self.session.add(menu)
    #     self.session.commit()
    #     return menu
    #
    # def update(self, menu_id: int, menu_data: SubmenuSchema, ) -> Submenu:
    #     menu = self._get(menu_id)
    #     for field, value in menu_data:
    #         setattr(menu, field, value)
    #     self.session.commit()
    #     return menu
    #
    # def delete(self, menu_id: int, ):
    #     menu = self._get(menu_id)
    #     self.session.delete(menu)
    #     self.session.commit()
    #
    # def _get(self, menu_id: int) -> Optional[Submenu]:
    #     menu = self.session.query(Submenu).filter(Submenu.id == menu_id).first()
    #     if not menu:
    #         raise HTTPException(status.HTTP_404_NOT_FOUND)
    #     return menu


class DishCRUD(AbstractCRUD):
    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session)
        self.model = Dish
