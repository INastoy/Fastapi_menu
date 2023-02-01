import uuid
from typing import List

from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from apps.menu.crud import DishCRUD
from apps.menu.schemas import DishBaseSchema, DishSchema

router = APIRouter(
    prefix='/menus/{menu_id}/submenus/{submenu_id}/dishes', tags=['dish'])


@router.get('/', response_model=List[DishSchema], status_code=HTTP_200_OK, summary='Список блюд подменю')
async def get_dishes(submenu_id: uuid.UUID, dish: DishCRUD = Depends()):
    """Возвращает список блюд указанного подменю"""
    return await dish.get_all(submenu_id)


@router.get('/{dish_id}', response_model=DishSchema, status_code=HTTP_200_OK, summary='Получить блюдо')
async def get_dish(submenu_id: uuid.UUID, dish_id: uuid.UUID, dish: DishCRUD = Depends()):
    """Возвращает указанное блюдо"""
    return await dish.get_by_id(dish_id, submenu_id)


@router.post('/', response_model=DishSchema, status_code=HTTP_201_CREATED, summary='Создать блюдо')
async def create_dish(submenu_id: uuid.UUID, dish_data: DishBaseSchema, menu_id: uuid.UUID, dish: DishCRUD = Depends()):
    """Создает новое блюдо"""
    return await dish.create(dish_data, submenu_id, menu_id)


@router.delete('/{dish_id}', status_code=HTTP_200_OK, summary='Удалить блюдо')
async def delete_dish(submenu_id: uuid.UUID, dish_id: uuid.UUID, menu_id: uuid.UUID, dish: DishCRUD = Depends()):
    """Удаляет указанное блюдо"""
    return await dish.delete(dish_id, submenu_id, menu_id)


@router.patch('/{dish_id}', response_model=DishSchema, summary='Обновить блюдо')
async def update_dish(submenu_id: uuid.UUID, dish_id: uuid.UUID, dish_data: DishBaseSchema, dish: DishCRUD = Depends()):
    """Обновляет указанное блюдо"""
    return await dish.update(dish_id, dish_data, submenu_id)
