from uuid import UUID

import pytest
from fastapi import HTTPException
from starlette.testclient import TestClient

from apps.menu.crud import MenuCRUD, SubmenuCRUD, DishCRUD
from apps.menu.models import Menu
from apps.menu.schemas import BaseSchema, MenuSchema
from core.database import get_session, Session


class TestMenu:
    def setup_class(self):
        self.session = next(get_session())
        self.session.add(Menu(title='test_title1', description='test_desc1'))
        self.session.commit()

        self.menu1 = (
            self.session.query(Menu)
                .filter_by(title='test_title1', description='test_desc1')
                .first()
        )

        self.data_for_create = dict(
            title='created_title', description='created_description'
        )
        self.data_for_update = dict(
            title='updated_title', description='updated_description'
        )
        self.menus_count = self.session.query(Menu).count()

    def test_get_menus_ok(self, client: TestClient, menu: MenuCRUD):
        response = client.get('/api/v1/menus/')
        menus_from_db = [MenuSchema.from_orm(menu) for menu in menu.get_all()]

        assert len(response.json()) == self.menus_count
        assert response.status_code == 200
        assert response.json() == menus_from_db

    def test_get_menu_ok(self, client: TestClient, menu: MenuCRUD):
        response = client.get(f'/api/v1/menus/{self.menu1.id}')
        menu_from_db: MenuSchema = MenuSchema.from_orm(
            menu.get_by_id(self.menu1.id))

        assert response.status_code == 200
        assert response.json() == menu_from_db

    def test_create_menu_ok(self, client: TestClient, menu: MenuCRUD, session: Session):
        response = client.post('/api/v1/menus/', json=self.data_for_create)
        menu_from_response = response.json()
        menu_id = UUID(menu_from_response.get('id'))
        menu_from_db = MenuSchema.from_orm(menu.get_by_id(menu_id))

        assert len(menu.get_all()) == self.menus_count + 1
        assert response.status_code == 201
        assert response.json() == menu_from_db

        created_menu = session.query(Menu).get(menu_id)
        session.delete(created_menu)
        session.commit()

    def test_update_menu_ok(self, client: TestClient, menu: MenuCRUD):
        response = client.patch(
            f'/api/v1/menus/{self.menu1.id}', json=self.data_for_update
        )
        menu_from_db = MenuSchema.from_orm(menu.get_by_id(self.menu1.id))

        assert response.status_code == 200
        assert response.json() == menu_from_db

    def test_delete_menu_ok(self, client: TestClient, menu: MenuCRUD):
        response = client.delete(f'/api/v1/menus/{self.menu1.id}')
        assert response.status_code == 200
        with pytest.raises(HTTPException) as ex:
            menu.get_by_id(self.menu1.id)
        assert ex.value.status_code == 404
        assert ex.value.detail == 'menu not found'

    def test_submenus_count_ok(self, client: TestClient, menu: MenuCRUD, submenu: SubmenuCRUD):
        new_menu = menu.create(
            BaseSchema(title='test_submenus_count',
                       description='test_submenus_count')
        )
        submenu.create(
            BaseSchema(title='test_submenus_count1',
                       description='test_submenus_count'),
            menu_id=new_menu.id,
        )
        submenu.create(
            BaseSchema(title='test_submenus_count2',
                       description='test_submenus_count'),
            menu_id=new_menu.id,
        )
        submenu.create(
            BaseSchema(title='test_submenus_count3',
                       description='test_submenus_count'),
            menu_id=new_menu.id,
        )
        refreshed_menu = menu.get_by_id(new_menu.id)

        assert refreshed_menu.submenus_count == 3

        menu.delete(new_menu.id)

    def test_dishes_count_ok(self, menu: MenuCRUD, submenu: SubmenuCRUD, dish: DishCRUD):
        new_menu = menu.create(
            BaseSchema(title='test_dishes_count',
                       description='test_dishes_count')
        )
        new_submenu = submenu.create(
            BaseSchema(title='test_dishes_count',
                       description='test_dishes_count'),
            menu_id=new_menu.id,
        )
        dish.create(
            BaseSchema(title='test_dishes_count1',
                       description='test_dishes_count'),
            submenu_id=new_submenu.id,
        )
        dish.create(
            BaseSchema(title='test_dishes_count2',
                       description='test_dishes_count'),
            submenu_id=new_submenu.id,
        )
        dish.create(
            BaseSchema(title='test_dishes_count3',
                       description='test_dishes_count'),
            submenu_id=new_submenu.id,
        )
        refreshed_menu = menu.get_by_id(new_menu.id)

        assert refreshed_menu.submenus_count == 1
        assert refreshed_menu.dishes_count == 3

        menu.delete(new_menu.id)

    def test_cascade_delete_ok(self, menu: MenuCRUD, submenu: SubmenuCRUD, dish: DishCRUD):
        new_menu = menu.create(
            BaseSchema(title='test_cascade_delete',
                       description='test_cascade_delete')
        )
        new_submenu = submenu.create(
            BaseSchema(title='test_cascade_delete',
                       description='test_cascade_delete'),
            menu_id=new_menu.id,
        )
        new_dish = dish.create(
            BaseSchema(title='test_cascade_del1',
                       description='test_cascade_del'),
            submenu_id=new_submenu.id,
        )
        new_menu_id = new_menu.id
        new_submenu_id = new_submenu.id
        new_dish_id = new_dish.id

        menu.delete(new_menu.id)

        with pytest.raises(HTTPException) as ex:
            submenu.get_by_id(submenu_id=new_submenu_id, menu_id=new_menu_id)
        assert ex.value.status_code == 404
        assert ex.value.detail == 'submenu not found'

        with pytest.raises(HTTPException) as ex:
            dish.get_by_id(dish_id=new_dish_id, submenu_id=new_submenu_id)
        assert ex.value.status_code == 404
        assert ex.value.detail == 'dish not found'

    def teardown_class(self):
        self.session.delete(self.menu1)
        self.session.commit()
        self.session.close()
        print('teardown')
