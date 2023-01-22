import uuid
from typing import List

from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from apps.menu.crud import DishCRUD
from apps.menu.schemas import DishSchema, BaseSchema, DishSchemaList

router = APIRouter(prefix='/menus/{menu_id}/submenus/{submenu_id}/dishes', tags=['dish'])


@router.get('/', response_model=List[DishSchemaList], status_code=HTTP_200_OK)
def get_dishes(submenu_id: uuid.UUID, dish: DishCRUD = Depends()):
    return dish.get_all(submenu_id)


@router.get('/{dish_id}', response_model=DishSchemaList, status_code=HTTP_200_OK)
def get_dish(submenu_id: uuid.UUID, dish_id: uuid.UUID, dish: DishCRUD = Depends()):
    return dish.get_by_id(dish_id, submenu_id)


@router.post('/', response_model=DishSchemaList, status_code=HTTP_201_CREATED)
def create_dish(submenu_id: str, dish_data: DishSchema, dish: DishCRUD = Depends()):
    return dish.create(dish_data, submenu_id)


# @router.delete('/{dish_id}', status_code=HTTP_204_NO_CONTENT)
@router.delete('/{dish_id}', status_code=HTTP_200_OK)
def delete_dish(submenu_id: uuid.UUID, dish_id: uuid.UUID, dish: DishCRUD = Depends()):
    return dish.delete(dish_id, submenu_id)


@router.patch('/{dish_id}', response_model=DishSchemaList)
def update_dish(submenu_id: uuid.UUID, dish_id: uuid.UUID, dish_data: DishSchema, dish: DishCRUD = Depends()):
    return dish.update(dish_id, dish_data, submenu_id)
