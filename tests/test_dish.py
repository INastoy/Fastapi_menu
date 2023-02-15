from decimal import Decimal
from uuid import UUID

import pytest
import pytest_asyncio
from fastapi import HTTPException
from httpx import AsyncClient
from sqlalchemy import func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.menu.crud import DishCRUD
from apps.menu.models import Dish, Menu, Submenu
from apps.menu.schemas import DishSchema

# def as_dict(model: Dish):
#     r = {column: str(getattr(model, column))
#          for column in model.__table__.c.keys()}
#     return r


@pytest.mark.asyncio
@pytest.mark.usefixtures('setup_class')
class TestDish:
    @pytest_asyncio.fixture
    async def setup_class(self, session: AsyncSession):
        self.session = session
        await self.session.execute(insert(Menu).values(title='dish_test_title1', description='dish_test_desc1'))
        self.menu1 = await self.session.scalar(
            select(Menu).filter_by(title='dish_test_title1',
                                   description='dish_test_desc1')
        )

        await self.session.execute(
            insert(Submenu).values(
                title='dish_test_title1',
                description='dish_test_desc1',
                menu_id=self.menu1.id,
            )
        )
        self.submenu1: Submenu = await self.session.scalar(
            select(Submenu).filter_by(
                title='dish_test_title1',
                description='dish_test_desc1',
                menu_id=self.menu1.id,
            )
        )

        await self.session.execute(
            insert(Dish).values(
                title='test_title1',
                description='test_desc1',
                price=12.34,
                submenu_id=self.submenu1.id,
            )
        )
        self.dish1: Dish = await self.session.scalar(
            select(Dish).filter_by(
                title='test_title1',
                description='test_desc1',
                price=Decimal('12.34'),
                submenu_id=self.submenu1.id,
            )
        )
        await self.session.commit()
        await self.session.refresh(self.menu1)
        await self.session.refresh(self.submenu1)
        await self.session.refresh(self.dish1)

        self.data_for_create = dict(
            title='created_title',
            description='created_desc',
            price=522.15,
            submenu_id=str(self.submenu1.id),
        )
        self.data_for_update = dict(
            title='updated_title', description='updated_desc', price=88.55)
        self.dishes_count = await self.session.scalar(
            select(func.count()).select_from(
                Dish).filter_by(submenu_id=self.submenu1.id)
        )

        # yield
        # await self.session.delete(self.menu1)
        # await self.session.delete(self.submenu1)
        # await self.session.delete(self.dish1)
        # await self.session.commit()
        # await self.session.close()
        # print('teardown')

    async def test_get_dishes_ok(self, client: AsyncClient, dish: DishCRUD):
        response = await client.get(
            f'/api/v1/menus/{self.menu1.id}/submenus/{self.submenu1.id}/dishes',
            follow_redirects=True,
        )
        dishes_from_db = [
            DishSchema.from_orm(dish_data) for dish_data in await dish.get_all(submenu_id=self.submenu1.id)
        ]
        assert len(response.json()) == self.dishes_count
        assert response.status_code == 200
        assert response.json() == dishes_from_db

    async def test_get_dish_ok(self, client: AsyncClient, dish: DishCRUD):
        response = await client.get(f'/api/v1/menus/{self.menu1.id}/submenus/{self.submenu1.id}/dishes/{self.dish1.id}')
        dish_from_db = DishSchema.from_orm(await dish.get_by_id(dish_id=self.dish1.id, submenu_id=self.submenu1.id))

        assert response.status_code == 200
        assert response.json() == dish_from_db

    async def test_create_dish_ok(self, client: AsyncClient, dish: DishCRUD):
        response = await client.post(
            f'/api/v1/menus/{self.menu1.id}/submenus/{self.submenu1.id}/dishes',
            json=self.data_for_create,
            follow_redirects=True,
        )
        dish_from_response = response.json()
        dish_id = UUID(dish_from_response.get('id'))
        dish_from_db = DishSchema.from_orm(await dish.get_by_id(dish_id=dish_id, submenu_id=self.submenu1.id))

        assert len(await dish.get_all(submenu_id=self.submenu1.id)) == self.dishes_count + 1

        assert response.status_code == 201
        assert dish_from_response == dish_from_db.dict()

    async def test_update_dish_ok(self, client: AsyncClient, session):
        old_dish = await session.scalar(select(Dish).filter_by(id=self.dish1.id, submenu_id=self.submenu1.id))
        assert DishSchema.from_orm(old_dish) == DishSchema.from_orm(self.dish1)
        response = await client.patch(
            f'/api/v1/menus/{self.menu1.id}/submenus/{self.submenu1.id}/dishes/{self.dish1.id}',
            json=self.data_for_update,
        )
        await self.session.refresh(old_dish)

        assert response.status_code == 200
        assert response.json() == DishSchema.from_orm(old_dish)

    async def test_delete_dish_ok(self, client: AsyncClient, dish: DishCRUD):
        response = await client.delete(
            f'/api/v1/menus/{self.menu1.id}/submenus/{self.submenu1.id}/dishes/{self.dish1.id}'
        )
        assert response.status_code == 200
        with pytest.raises(HTTPException) as ex:
            await dish.get_by_id(dish_id=self.dish1.id, submenu_id=self.submenu1.id)

        assert ex.value.status_code == 404
        assert ex.value.detail == 'dish not found'

    # async def teardown_class(self):
    #     await self.session.delete(self.menu1)
    #     await self.session.delete(self.submenu1)
    #     await self.session.delete(self.dish1)
    #     await self.session.commit()
    #     await self.session.close()
    #     print('teardown')
