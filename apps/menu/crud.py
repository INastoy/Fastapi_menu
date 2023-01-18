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

    def get_all(self, *args, **kwargs) -> List[Type[Base]]:
        return self.session.query(self.model).all()

    def get_by_id(self, item_id: str, *args, **kwargs) -> Type[Base]:
        return self._get(item_id)

    def create(self, item_data: BaseSchema, *args, **kwargs) -> Type[Base]:
        item = self.model(**item_data.dict())
        self.session.add(item)
        self.session.commit()
        return item

    def update(self, item_id: str, item_data: BaseSchema, *args, **kwargs) -> Type[Base]:
        item = self._get(item_id)
        for field, value in item_data:
            setattr(item, field, value)
        self.session.commit()
        return item

    def delete(self, item_id: str, *args, **kwargs):
        item = self._get(item_id)
        self.session.delete(item)
        self.session.commit()

    def _get(self, item_id: str, *args, **kwargs) -> Optional[Type[Base]]:
        if len(item_id) != 36:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        item = self.session.query(self.model).filter(self.model.id == item_id).first()
        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='menu not found')
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

    def get_by_id(self, item_id: str, *args, **kwargs) -> Type[Base]:
        item = self.session.query(
            Menu.id,
            Menu.title,
            Menu.description,
            func.count(distinct(Submenu.id)).label('submenus_count'),
            func.count(distinct(Dish.id)).label('dishes_count'))\
            .outerjoin(Submenu, Menu.id == Submenu.menu_id)\
            .outerjoin(Dish, Submenu.id == Dish.submenu_id)\
            .group_by(Menu.id)\
            .first()
        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='menu not found')
        return item
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

    def get_all(self, menu_id: str) -> List[Submenu]:
        return self.session.query(
            Submenu.id,
            Submenu.title,
            Submenu.description,
            func.count(distinct(Dish.id)).label('dishes_count'))\
            .outerjoin(Dish, Submenu.id == Dish.submenu_id)\
            .filter(Submenu.menu_id == menu_id)\
            .group_by(Submenu.id)\
            .all()

    def create(self, item_data: BaseSchema, menu_id: str) -> Type[Base]:
        item = self.model(**item_data.dict(), menu_id=menu_id)
        self.session.add(item)
        self.session.commit()
        return item

    def delete(self, item_id: str, menu_id: str, *args, **kwargs):
        item = self._get(item_id, menu_id)
        self.session.delete(item)
        self.session.commit()

    def get_by_id(self, submenu_id: str, menu_id: str, *args, **kwargs) -> Type[Base]:
        item = self.session.query(
            Submenu.id,
            Submenu.title,
            Submenu.description,
            func.count(distinct(Dish.id)).label('dishes_count'))\
            .outerjoin(Dish, Submenu.id == Dish.submenu_id)\
            .filter(Submenu.menu_id == menu_id)\
            .group_by(Submenu.id)\
            .first()
        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='submenu not found')
        return item

    def update(self, item_id: str, item_data: BaseSchema, menu_id: str, *args, **kwargs) -> Type[Base]:
        item = self._get(item_id, menu_id)
        for field, value in item_data:
            setattr(item, field, value)
        self.session.commit()
        return item

    def _get(self, submenu_id: str, menu_id: str) -> Optional[Submenu]:
        if len(submenu_id) != 36:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        menu = self.session.query(Submenu)\
            .filter(Submenu.id == submenu_id)\
            .filter(Menu.id == menu_id)\
            .join(Menu, Menu.id == menu_id)\
            .first()
        if not menu:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='submenu not found')
        return menu


class DishCRUD(AbstractCRUD):
    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(session)
        self.model = Dish

    def get_all(self, submenu_id: str) -> List[Submenu]:
        return self.session.query(Dish)\
            .filter(Dish.submenu_id == submenu_id)\
            .all()

    def create(self, item_data: BaseSchema, submenu_id: str) -> Type[Base]:
        item = self.model(**item_data.dict(), submenu_id=submenu_id)
        self.session.add(item)
        self.session.commit()
        return item

    def delete(self, item_id: str, submenu_id: str, *args, **kwargs):
        item = self._get(item_id, submenu_id)
        self.session.delete(item)
        self.session.commit()

    def get_by_id(self, item_id: str, submenu_id: str, *args, **kwargs) -> Type[Base]:
        return self._get(item_id, submenu_id)

    def update(self, item_id: str, item_data: BaseSchema, submenu_id: str, *args, **kwargs) -> Type[Base]:
        item = self._get(item_id, submenu_id)
        for field, value in item_data:
            setattr(item, field, value)
        self.session.commit()
        return item

    def _get(self, dish_id: str, submenu_id: str) -> Optional[Submenu]:
        if len(dish_id) != 36:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        dish = self.session.query(Dish)\
            .filter(Dish.id == dish_id)\
            .filter(Submenu.id == submenu_id) \
            .join(Submenu, Submenu.id == submenu_id) \
            .first()
        if not dish:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='dish not found')
        return dish