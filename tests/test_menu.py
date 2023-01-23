import pytest
from fastapi import HTTPException

from apps.menu.models import Menu
from apps.menu.schemas import BaseSchema, MenuSchema
from core.database import get_session


class TestMenu:

    def setup_class(self):
        self.session = next(get_session())
        self.session.add(Menu(title='test_title1', description='test_desc1'))
        # self.menu2 = self.session.add(Menu(title='test_title2', description='test_desc2'))
        self.session.commit()

        self.menu1 = self.session.query(Menu).filter_by(title='test_title1', description='test_desc1').first()

        self.data_for_create = dict(title='created_title', description='created_description')
        self.data_for_update = dict(title='updated_title', description='updated_description')

    def test_get_menus_ok(self, client, menu):
        response = client.get('/api/v1/menus/')
        menus_from_response = [MenuSchema(**menu) for menu in response.json()]
        menus_from_db = [MenuSchema(**menu) for menu in menu.get_all()]

        assert response.status_code == 200
        assert menus_from_response == menus_from_db

    def test_get_menu_ok(self, client, menu, session):
        response = client.get(f'/api/v1/menus/{self.menu1.id}')
        menu_from_response = MenuSchema(**response.json())
        menu_from_db: MenuSchema = MenuSchema(**menu.get_by_id(self.menu1.id))

        assert response.status_code == 200
        assert menu_from_response == menu_from_db

    def test_create_menu_ok(self, client, menu):
        response = client.post('/api/v1/menus/', json=self.data_for_create)
        menu_from_response = MenuSchema(**response.json())
        menu_from_db = MenuSchema(**menu.get_by_id(menu_from_response.id))

        assert response.status_code == 201
        assert menu_from_response == menu_from_db

    def test_update_menu_ok(self, client, menu, session):
        random_menu: Menu = session.query(Menu).first()
        response = client.patch(f'/api/v1/menus/{random_menu.id}', json=self.data_for_update)
        menu_from_response = BaseSchema(**response.json())
        session.refresh(random_menu)
        menu_from_db = BaseSchema(**menu.get_by_id(random_menu.id))

        assert response.status_code == 200
        assert menu_from_response == menu_from_db

    def test_delete_menu_ok(self, client, menu, session):
        random_menu: Menu = session.query(Menu).first()
        response = client.delete(f'/api/v1/menus/{random_menu.id}')
        assert response.status_code == 200
        with pytest.raises(HTTPException) as ex:
            menu_from_db = menu.get_by_id(random_menu.id)
        assert ex.value.status_code == 404
        assert ex.value.detail == 'menu not found'

    def teardown_class(self):
        self.session.delete(self.menu1)
        self.session.commit()
        self.session.close()
        print('teardown')
