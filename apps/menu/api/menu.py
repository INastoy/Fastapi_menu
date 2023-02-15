import uuid

from fastapi import APIRouter, Depends
from starlette.responses import FileResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_202_ACCEPTED

from apps.menu.schemas import BaseSchema, MenuSchema
from apps.menu.services import MenuService
from core.openapi.responses import RESPONSE_303, RESPONSE_404

router = APIRouter(prefix='/menus', tags=['menu'])


@router.get('/', response_model=list[MenuSchema], status_code=HTTP_200_OK, summary='Список меню')
async def get_menus(menu: MenuService = Depends()):
    """Возвращает список всех меню с количеством всех подменю и блюд"""
    return await menu.get_all()


@router.get(
    '/{menu_id}',
    response_model=MenuSchema,
    status_code=HTTP_200_OK,
    summary='Получить меню',
    responses=RESPONSE_404,
)
async def get_menu(menu_id: uuid.UUID, menu: MenuService = Depends()):
    """Возвращает меню с количеством всех подменю и блюд"""
    return await menu.get_by_id(menu_id)


@router.post(
    '/', response_model=MenuSchema, status_code=HTTP_201_CREATED, summary='Создать меню', responses=RESPONSE_303
)
async def create_menu(menu_data: BaseSchema, menu: MenuService = Depends()):
    """Создает новое меню"""
    return await menu.create(menu_data)


@router.delete('/{menu_id}', status_code=HTTP_200_OK, summary='Удалить меню', responses=RESPONSE_404)
async def delete_menu(menu_id: uuid.UUID, menu: MenuService = Depends()):
    """Удаляет указанное меню"""
    return await menu.delete(menu_id)


@router.patch('/{menu_id}', response_model=MenuSchema, summary='Обновить меню', responses=RESPONSE_404)
async def update_menu(menu_id: uuid.UUID, menu_data: BaseSchema, menu: MenuService = Depends()):
    """Обновляет указанное меню"""
    return await menu.update(menu_id, menu_data)


@router.post(
    '/menus/fill',
    status_code=HTTP_201_CREATED,
    summary='Заполняет базу тестовыми данными',
)
async def fill_menus(menu: MenuService = Depends()):
    """Создает тестовые меню, подменю и блюда на основе .json файла"""
    return await menu.create_example(file_path='core/example_db_filler.json')


@router.post(
    '/menus/generate_excel',
    status_code=HTTP_202_ACCEPTED,
    summary='Сгенерировать .xlsx файл с меню',
)
async def generate_excel(menu: MenuService = Depends()):
    """Генерирует пример заполненного меню с подменю и блюдами.
    При вызове возвращает id, по которому можно получить файл через эндпоинт get_excel
    """
    return await menu.generate_excel()


@router.get(
    '/menus/get_excel',
    response_class=FileResponse,
    status_code=HTTP_200_OK,
    summary='Скачать Меню.xlsx',
    responses=RESPONSE_404,
)
async def get_excel(file_id: uuid.UUID, menu: MenuService = Depends()):
    """Возвращает Excel файл с текущими меню, подменю и блюдами.
    Для получения файла требуется получить file_id в энпоинте gen_excel.
    После выполнения сгенерированный файл удаляется с сервера"""
    return await menu.get_excel(file_id)
