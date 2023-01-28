import pytest
from fastapi import HTTPException
from starlette.testclient import TestClient

from apps.menu.crud import SubmenuCRUD
from apps.menu.models import Menu, Submenu
from apps.menu.schemas import SubmenuSchema
from core.database import get_session


class TestSubmenu:
    def setup_class(self):
        self.session = next(get_session())
        self.session.add(
            Menu(title='submenu_test_title1', description='submenu_test_desc1')
        )
        self.session.commit()
        self.menu1: Menu = (
            self.session.query(Menu)
                .filter(
                Menu.title == 'submenu_test_title1',
                Menu.description == 'submenu_test_desc1',
            )
            .first()
        )

        self.session.add(
            Submenu(
                title='test_title1', description='test_desc1', menu_id=self.menu1.id
            )
        )
        self.session.commit()
        self.submenu1: Submenu = (
            self.session.query(Submenu)
                .filter_by(
                title='test_title1', description='test_desc1', menu_id=self.menu1.id
            )
            .first()
        )

        self.data_for_create = dict(
            title='created_title',
            description='created_desc',
            menu_id=str(self.menu1.id),
        )
        self.data_for_update = dict(
            title='updated_title', description='updated_desc')
        self.submenus_count = (
            self.session.query(Submenu).filter(
                Submenu.menu_id == self.menu1.id).count()
        )

    def test_get_submenus_ok(self, client: TestClient, submenu: SubmenuCRUD):
        response = client.get(f'/api/v1/menus/{self.menu1.id}/submenus')
        submenus_from_db = [
            SubmenuSchema.from_orm(submenu)
            for submenu in submenu.get_all(menu_id=self.menu1.id)
        ]

        assert len(response.json()) == self.submenus_count
        assert response.status_code == 200
        assert response.json() == submenus_from_db

    def test_get_submenu_ok(self, client: TestClient, submenu: SubmenuCRUD):
        response = client.get(
            f'/api/v1/menus/{self.menu1.id}/submenus/{self.submenu1.id}'
        )
        submenu_from_db = SubmenuSchema.from_orm(
            submenu.get_by_id(submenu_id=self.submenu1.id,
                              menu_id=self.menu1.id)
        )

        assert response.status_code == 200
        assert response.json() == submenu_from_db

    def test_create_submenu_ok(self, client: TestClient, submenu: SubmenuCRUD):
        response = client.post(
            f'/api/v1/menus/{self.menu1.id}/submenus/', json=self.data_for_create
        )
        submenu_from_response = SubmenuSchema(**response.json())
        submenu_from_db = SubmenuSchema.from_orm(
            submenu.get_by_id(submenu_id=submenu_from_response.id, menu_id=self.menu1.id))

        assert len(submenu.get_all(self.menu1.id)) == self.submenus_count + 1
        assert response.status_code == 201
        assert submenu_from_response == submenu_from_db

    def test_update_submenu_ok(self, client: TestClient, submenu: SubmenuCRUD):
        response = client.patch(
            f'/api/v1/menus/{self.menu1.id}/submenus/{self.submenu1.id}',
            json=self.data_for_update,
        )
        submenu_from_db = SubmenuSchema.from_orm(
            submenu.get_by_id(submenu_id=self.submenu1.id,
                              menu_id=self.menu1.id)
        )

        assert response.status_code == 200
        assert submenu_from_db.title == self.data_for_update.get('title')
        assert submenu_from_db.description == self.data_for_update.get(
            'description')
        assert response.json() == submenu_from_db

    def test_delete_submenu_ok(self, client: TestClient, submenu: SubmenuCRUD):
        response = client.delete(
            f'/api/v1/menus/{self.menu1.id}/submenus/{self.submenu1.id}'
        )
        assert response.status_code == 200
        with pytest.raises(HTTPException) as ex:
            submenu.get_by_id(submenu_id=self.submenu1.id,
                              menu_id=self.menu1.id)

        assert ex.value.status_code == 404
        assert ex.value.detail == 'submenu not found'

    def teardown_class(self):
        self.session.delete(self.menu1)
        self.session.delete(self.submenu1)
        self.session.commit()
        self.session.close()
        print('teardown')
