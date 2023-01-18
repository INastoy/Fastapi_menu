from typing import List

from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from apps.menu.crud import SubmenuCRUD
from apps.menu.schemas import SubmenuSchema, BaseSchema

router = APIRouter(prefix='/{menu_id}/submenus', tags=['submenu'])


@router.get('/', response_model=List[SubmenuSchema], status_code=HTTP_200_OK)
def get_submenus(submenu: SubmenuCRUD = Depends()):
    return submenu.get_all()


@router.get('/{submenu_id}', response_model=SubmenuSchema, status_code=HTTP_200_OK)
def get_submenu(submenu_id: str, submenu: SubmenuCRUD = Depends()):
    return submenu.get_by_id(submenu_id)


@router.post('/', response_model=SubmenuSchema, status_code=HTTP_201_CREATED)
def create_submenu(submenu_data: BaseSchema, submenu: SubmenuCRUD = Depends()):
    return submenu.create(submenu_data)


@router.delete('/{submenu_id}', status_code=HTTP_204_NO_CONTENT)
async def delete_submenu(submenu_id: str, submenu: SubmenuCRUD = Depends()):
    return submenu.delete(submenu_id)


@router.patch('/{submenu_id}', response_model=SubmenuSchema)
async def update_submenu(submenu_id: str, submenu_data: BaseSchema, submenu: SubmenuCRUD = Depends()):
    return submenu.update(submenu_id, submenu_data)
