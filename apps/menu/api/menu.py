import uuid
from typing import List

from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from apps.menu.crud import MenuCRUD
from apps.menu.schemas import BaseSchema, MenuSchema

router = APIRouter(prefix='/menus', tags=['menu'])


@router.get('/', response_model=List[MenuSchema], status_code=HTTP_200_OK, summary='Список меню')
def get_menus(menu: MenuCRUD = Depends()):
    """Возвращает список всех меню с количеством всех подменю и блюд"""
    return menu.get_all()


@router.get('/{menu_id}', response_model=MenuSchema, status_code=HTTP_200_OK, summary='Получить меню')
def get_menu(menu_id: uuid.UUID, menu: MenuCRUD = Depends()):
    """Возвращает меню с количеством всех подменю и блюд"""
    return menu.get_by_id(menu_id)


@router.post('/', response_model=MenuSchema, status_code=HTTP_201_CREATED, summary='Создать меню')
def create_menu(menu_data: BaseSchema, menu: MenuCRUD = Depends()):
    """Создает новое меню"""
    return menu.create(menu_data)


@router.delete('/{menu_id}', status_code=HTTP_200_OK, summary='Удалить меню')
async def delete_menu(menu_id: uuid.UUID, menu: MenuCRUD = Depends()):
    """Удаляет указанное меню"""
    return menu.delete(menu_id)


@router.patch('/{menu_id}', response_model=MenuSchema, summary='Обновить меню')
async def update_menu(menu_id: uuid.UUID, menu_data: BaseSchema, menu: MenuCRUD = Depends()):
    """Обновляет указанное меню"""
    return menu.update(menu_id, menu_data)
