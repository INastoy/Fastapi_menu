import uuid

from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from apps.menu.schemas import DishBaseSchema, DishSchema
from apps.menu.services import DishService
from core.openapi.responses import RESPONSE_303, RESPONSE_404

router = APIRouter(
    prefix='/menus/{menu_id}/submenus/{submenu_id}/dishes', tags=['dish'])


@router.get(
    '/',
    response_model=list[DishSchema],
    status_code=HTTP_200_OK,
    summary='Список блюд подменю',
)
async def get_dishes(submenu_id: uuid.UUID, dish: DishService = Depends()):
    """Возвращает список блюд указанного подменю"""
    return await dish.get_all(submenu_id)


@router.get(
    '/{dish_id}',
    response_model=DishSchema,
    status_code=HTTP_200_OK,
    summary='Получить блюдо',
    responses=RESPONSE_404,
)
async def get_dish(submenu_id: uuid.UUID, dish_id: uuid.UUID, dish: DishService = Depends()):
    """Возвращает указанное блюдо"""
    return await dish.get_by_id(dish_id, submenu_id)


@router.post(
    '/',
    response_model=DishSchema,
    status_code=HTTP_201_CREATED,
    summary='Создать блюдо',
    responses=RESPONSE_303,
)
async def create_dish(
    submenu_id: uuid.UUID,
    dish_data: DishBaseSchema,
    menu_id: uuid.UUID,
    dish: DishService = Depends(),
):
    """Создает новое блюдо"""
    return await dish.create(dish_data, submenu_id, menu_id)


@router.delete('/{dish_id}', status_code=HTTP_200_OK, summary='Удалить блюдо', responses=RESPONSE_404)
async def delete_dish(
    submenu_id: uuid.UUID,
    dish_id: uuid.UUID,
    menu_id: uuid.UUID,
    dish: DishService = Depends(),
):
    """Удаляет указанное блюдо"""
    return await dish.delete(dish_id, submenu_id, menu_id)


@router.patch('/{dish_id}', response_model=DishSchema, summary='Обновить блюдо', responses=RESPONSE_404)
async def update_dish(
    submenu_id: uuid.UUID,
    dish_id: uuid.UUID,
    menu_id: uuid.UUID,
    dish_data: DishBaseSchema,
    dish: DishService = Depends(),
):
    """Обновляет указанное блюдо"""
    return await dish.update(dish_id, dish_data, submenu_id, menu_id)
