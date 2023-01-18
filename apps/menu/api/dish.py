from typing import List

from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from apps.menu.crud import DishCRUD
from apps.menu.schemas import DishSchema, BaseSchema

router = APIRouter(prefix='/{menu_id}/submenus/{submenu_id}/dishes', tags=['dish'])


@router.get('/', response_model=List[DishSchema], status_code=HTTP_200_OK)
def get_dishes(dish: DishCRUD = Depends()):
    return dish.get_all()


@router.get('/{dish_id}', response_model=DishSchema, status_code=HTTP_200_OK)
def get_dish(dish_id: str, dish: DishCRUD = Depends()):
    return dish.get_by_id(dish_id)


@router.post('/', response_model=DishSchema, status_code=HTTP_201_CREATED)
def create_dish(dish_data: BaseSchema, dish: DishCRUD = Depends()):
    return dish.create(dish_data)


@router.delete('/{dish_id}', status_code=HTTP_204_NO_CONTENT)
def delete_dish(dish_id: str, dish: DishCRUD = Depends()):
    return dish.delete(dish_id)


@router.patch('/{dish_id}', response_model=DishSchema)
def update_dish(dish_id: str, dish_data: BaseSchema, dish: DishCRUD = Depends()):
    return dish.update(dish_id, dish_data)
