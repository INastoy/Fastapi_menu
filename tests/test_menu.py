from uuid import UUID

import pytest
import pytest_asyncio
from fastapi import HTTPException
from httpx import AsyncClient
from sqlalchemy import select, insert, func
from sqlalchemy.ext.asyncio import AsyncSession

from apps.menu.crud import MenuCRUD, SubmenuCRUD, DishCRUD
from apps.menu.models import Menu
from apps.menu.schemas import BaseSchema, MenuSchema


@pytest.mark.asyncio
@pytest.mark.usefixtures('setup_class')
class TestMenu:

    @pytest_asyncio.fixture
    async def setup_class(self, session: AsyncSession):
        self.session = session
        await self.session.execute(insert(Menu).values(title='test_title1', description='test_desc1'))
        await self.session.commit()

        self.menu1 = await self.session.scalar(select(Menu).filter_by(title='test_title1', description='test_desc1'))

        self.data_for_create = dict(
            title='created_title', description='created_description')
        self.data_for_update = dict(
            title='updated_title', description='updated_description')
        self.menus_count = await self.session.scalar(select(func.count()).select_from(Menu))
        yield

        await session.delete(self.menu1)
        await session.commit()
        await session.close()
        print('teardown')

    async def test_get_menus_ok(self, client: AsyncClient, menu: MenuCRUD):
        response = await client.get('/api/v1/menus/')
        menus_from_db = [MenuSchema.from_orm(menu) for menu in await menu.get_all()]

        assert len(response.json()) == self.menus_count
        assert response.status_code == 200
        assert response.json() == menus_from_db

    async def test_get_menu_ok(self, client: AsyncClient, menu: MenuCRUD):
        response = await client.get(f'/api/v1/menus/{self.menu1.id}')
        menu_from_db: MenuSchema = MenuSchema.from_orm(await menu.get_by_id(self.menu1.id))

        assert response.status_code == 200
        assert response.json() == menu_from_db

    async def test_create_menu_ok(self, client: AsyncClient, menu: MenuCRUD, session: AsyncSession):
        response = await client.post('/api/v1/menus/', json=self.data_for_create)
        menu_from_response = response.json()
        menu_id = UUID(menu_from_response.get('id'))
        menu_from_db = MenuSchema.from_orm(await menu.get_by_id(menu_id))

        assert len(await menu.get_all()) == self.menus_count + 1
        assert response.status_code == 201
        assert response.json() == menu_from_db

        created_menu = await session.get(Menu, menu_id)
        await session.delete(created_menu)
        await session.commit()

    async def test_update_menu_ok(self, client: AsyncClient, menu: MenuCRUD):
        response = await client.patch(
            f'/api/v1/menus/{self.menu1.id}', json=self.data_for_update
        )
        menu_from_db = MenuSchema.from_orm(await menu.get_by_id(self.menu1.id))

        assert response.status_code == 200
        assert response.json() == menu_from_db

    async def test_delete_menu_ok(self, client: AsyncClient, menu: MenuCRUD):
        response = await client.delete(f'/api/v1/menus/{self.menu1.id}')
        assert response.status_code == 200
        with pytest.raises(HTTPException) as ex:
            await menu.get_by_id(self.menu1.id)
        assert ex.value.status_code == 404
        assert ex.value.detail == 'menu not found'

    async def test_submenus_count_ok(self, menu: MenuCRUD, submenu: SubmenuCRUD):
        new_menu = await menu.create(
            BaseSchema(title='test_submenus_count',
                       description='test_submenus_count')
        )
        await submenu.create(
            BaseSchema(title='test_submenus_count1',
                       description='test_submenus_count'),
            menu_id=new_menu.id,
        )
        await submenu.create(
            BaseSchema(title='test_submenus_count2',
                       description='test_submenus_count'),
            menu_id=new_menu.id,
        )
        await submenu.create(
            BaseSchema(title='test_submenus_count3',
                       description='test_submenus_count'),
            menu_id=new_menu.id,
        )
        refreshed_menu = await menu.get_by_id(new_menu.id)

        assert refreshed_menu.submenus_count == 3

        await menu.delete(new_menu.id)

    async def test_dishes_count_ok(self, menu: MenuCRUD, submenu: SubmenuCRUD, dish: DishCRUD):
        new_menu = await menu.create(
            BaseSchema(title='test_dishes_count',
                       description='test_dishes_count')
        )
        new_submenu = await submenu.create(
            BaseSchema(title='test_dishes_count',
                       description='test_dishes_count'),
            menu_id=new_menu.id,
        )
        await dish.create(
            BaseSchema(title='test_dishes_count1',
                       description='test_dishes_count'),
            submenu_id=new_submenu.id,
        )
        await dish.create(
            BaseSchema(title='test_dishes_count2',
                       description='test_dishes_count'),
            submenu_id=new_submenu.id,
        )
        await dish.create(
            BaseSchema(title='test_dishes_count3',
                       description='test_dishes_count'),
            submenu_id=new_submenu.id,
        )
        refreshed_menu = await menu.get_by_id(new_menu.id)

        assert refreshed_menu.submenus_count == 1
        assert refreshed_menu.dishes_count == 3

        await menu.delete(new_menu.id)

    async def test_cascade_delete_ok(self, menu: MenuCRUD, submenu: SubmenuCRUD, dish: DishCRUD):
        new_menu = await menu.create(
            BaseSchema(title='test_cascade_delete',
                       description='test_cascade_delete')
        )
        new_submenu = await submenu.create(
            BaseSchema(title='test_cascade_delete',
                       description='test_cascade_delete'),
            menu_id=new_menu.id,
        )
        new_dish = await dish.create(
            BaseSchema(title='test_cascade_del1',
                       description='test_cascade_del'),
            submenu_id=new_submenu.id,
        )
        new_menu_id = new_menu.id
        new_submenu_id = new_submenu.id
        new_dish_id = new_dish.id

        await menu.delete(new_menu.id)

        with pytest.raises(HTTPException) as ex:
            await submenu.get_by_id(submenu_id=new_submenu_id, menu_id=new_menu_id)
        assert ex.value.status_code == 404
        assert ex.value.detail == 'submenu not found'

        with pytest.raises(HTTPException) as ex:
            await dish.get_by_id(dish_id=new_dish_id, submenu_id=new_submenu_id)
        assert ex.value.status_code == 404
        assert ex.value.detail == 'dish not found'

    # async def teardown_class(self):
    #     await self.session.delete(self.menu1)
    #     await self.session.commit()
    #     await self.session.close()
    #     print('teardown')
