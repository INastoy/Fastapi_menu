import uuid
from typing import List

from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from apps.menu.crud import SubmenuCRUD
from apps.menu.schemas import SubmenuSchema, BaseSchema, SubmenuSchema

router = APIRouter(prefix='/menus/{menu_id}/submenus', tags=['submenu'])


@router.get('/', response_model=List[SubmenuSchema], status_code=HTTP_200_OK)
# @router.get('/', status_code=HTTP_200_OK)
def get_submenus(menu_id: str, submenu: SubmenuCRUD = Depends()):
    return submenu.get_all(menu_id)


@router.get('/{submenu_id}', response_model=SubmenuSchema, status_code=HTTP_200_OK)
def get_submenu(menu_id: uuid.UUID, submenu_id: uuid.UUID, submenu: SubmenuCRUD = Depends()):
    return submenu.get_by_id(submenu_id, menu_id)


@router.post('/', response_model=SubmenuSchema, status_code=HTTP_201_CREATED)
def create_submenu(menu_id: str, submenu_data: BaseSchema, submenu: SubmenuCRUD = Depends()):
    return submenu.create(submenu_data, menu_id)


# @router.delete('/{submenu_id}', status_code=HTTP_204_NO_CONTENT)
@router.delete('/{submenu_id}', status_code=HTTP_200_OK)
async def delete_submenu(menu_id: uuid.UUID, submenu_id: uuid.UUID, submenu: SubmenuCRUD = Depends()):
    return submenu.delete(submenu_id, menu_id)


@router.patch('/{submenu_id}', response_model=SubmenuSchema)
async def update_submenu(menu_id: uuid.UUID, submenu_id: uuid.UUID, submenu_data: BaseSchema, submenu: SubmenuCRUD = Depends()):
    return submenu.update(submenu_id, submenu_data, menu_id)
