from typing import List

from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from apps.menu.crud import MenuCRUD
from apps.menu.schemas import MenuSchemaList, BaseSchema, MenuSchema

router = APIRouter(prefix='/menus', tags=['menu'])


@router.get('/', response_model=List[MenuSchemaList], status_code=HTTP_200_OK)
def get_menus(menu: MenuCRUD = Depends()):
    return menu.get_all()


# @router.get('/{menu_id}', response_model=MenuSchema, status_code=HTTP_200_OK)
@router.get('/{menu_id}', status_code=HTTP_200_OK)
def get_menu(menu_id: str, menu: MenuCRUD = Depends()):
    return menu.get_by_id(menu_id)


@router.post('/', response_model=MenuSchema, status_code=HTTP_201_CREATED)
def create_menu(menu_data: BaseSchema, menu: MenuCRUD = Depends()):
    return menu.create(menu_data)


# @router.delete('/{menu_id}', status_code=HTTP_204_NO_CONTENT)
@router.delete('/{menu_id}', status_code=HTTP_200_OK)
async def delete_menu(menu_id: str, menu: MenuCRUD = Depends()):
    return menu.delete(menu_id)


@router.patch('/{menu_id}', response_model=MenuSchema)
async def update_menu(menu_id: str, menu_data: BaseSchema, menu: MenuCRUD = Depends()):
    return menu.update(menu_id, menu_data)
