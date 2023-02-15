import pytest
import pytest_asyncio
from fastapi import HTTPException
from httpx import AsyncClient
from sqlalchemy import func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.menu.crud import SubmenuCRUD
from apps.menu.models import Menu, Submenu
from apps.menu.schemas import SubmenuSchema


@pytest.mark.asyncio
@pytest.mark.usefixtures('setup_class')
class TestSubmenu:
    @pytest_asyncio.fixture
    async def setup_class(self, session: AsyncSession):
        self.session = session
        await self.session.execute(insert(Menu).values(title='submenu_test_title1', description='submenu_test_desc1'))

        self.menu1 = await self.session.scalar(
            select(Menu).filter_by(title='submenu_test_title1',
                                   description='submenu_test_desc1')
        )

        await self.session.execute(
            insert(Submenu).values(title='test_title1',
                                   description='test_desc1', menu_id=self.menu1.id)
        )
        await self.session.commit()
        await self.session.refresh(self.menu1)

        self.submenu1: Submenu = await self.session.scalar(
            select(Submenu).filter_by(title='test_title1',
                                      description='test_desc1', menu_id=self.menu1.id)
        )

        self.data_for_create = dict(
            title='created_title',
            description='created_desc',
            menu_id=str(self.menu1.id),
        )
        self.data_for_update = dict(
            title='updated_title', description='updated_desc')
        self.submenus_count = await self.session.scalar(
            select(func.count()).select_from(
                Submenu).filter_by(menu_id=self.menu1.id)
        )

    async def test_get_submenus_ok(self, client: AsyncClient, submenu: SubmenuCRUD):
        response = await client.get(f'/api/v1/menus/{self.menu1.id}/submenus', follow_redirects=True)
        submenus_from_db = [SubmenuSchema.from_orm(submenu) for submenu in await submenu.get_all(menu_id=self.menu1.id)]

        assert len(response.json()) == self.submenus_count
        assert response.status_code == 200
        assert response.json() == submenus_from_db

    async def test_get_submenu_ok(self, client: AsyncClient, submenu: SubmenuCRUD):
        response = await client.get(f'/api/v1/menus/{self.menu1.id}/submenus/{self.submenu1.id}')
        submenu_from_db = SubmenuSchema.from_orm(
            await submenu.get_by_id(submenu_id=self.submenu1.id, menu_id=self.menu1.id)
        )

        assert response.status_code == 200
        assert response.json() == submenu_from_db

    async def test_create_submenu_ok(self, client: AsyncClient, submenu: SubmenuCRUD):
        response = await client.post(f'/api/v1/menus/{self.menu1.id}/submenus/', json=self.data_for_create)
        submenu_from_response = SubmenuSchema(**response.json())
        submenu_from_db = SubmenuSchema.from_orm(
            await submenu.get_by_id(submenu_id=submenu_from_response.id, menu_id=self.menu1.id)
        )

        assert len(await submenu.get_all(self.menu1.id)) == self.submenus_count + 1
        assert response.status_code == 201
        assert submenu_from_response == submenu_from_db

    async def test_update_submenu_ok(self, client: AsyncClient, submenu: SubmenuCRUD):
        response = await client.patch(
            f'/api/v1/menus/{self.menu1.id}/submenus/{self.submenu1.id}',
            json=self.data_for_update,
        )
        submenu_from_db = SubmenuSchema.from_orm(
            await submenu.get_by_id(submenu_id=self.submenu1.id, menu_id=self.menu1.id)
        )

        assert response.status_code == 200
        assert submenu_from_db.title == self.data_for_update.get('title')
        assert submenu_from_db.description == self.data_for_update.get(
            'description')
        assert response.json() == submenu_from_db

    async def test_delete_submenu_ok(self, client: AsyncClient, submenu: SubmenuCRUD):
        response = await client.delete(f'/api/v1/menus/{self.menu1.id}/submenus/{self.submenu1.id}')
        assert response.status_code == 200
        with pytest.raises(HTTPException) as ex:
            await submenu.get_by_id(submenu_id=self.submenu1.id, menu_id=self.menu1.id)

        assert ex.value.status_code == 404
        assert ex.value.detail == 'submenu not found'

    # async def teardown_class(self):
    #     await self.session.delete(self.menu1)
    #     await self.session.delete(self.submenu1)
    #     await self.session.commit()
    #     await self.session.close()
    #     print('teardown')
