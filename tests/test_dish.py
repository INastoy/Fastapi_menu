import pytest
from fastapi import HTTPException

from apps.menu.models import Menu, Submenu, Dish
from apps.menu.schemas import DishSchema
from core.database import get_session


def as_dict(model: Dish):
    r = {column: str(getattr(model, column)) for column in model.__table__.c.keys()}
    return r


class TestDish:

    def setup_class(self):
        self.session = next(get_session())
        self.session.add(Menu(title='dish_test_title1', description='dish_test_desc1'))
        self.session.commit()
        self.menu1: Menu = self.session.query(Menu) \
            .filter(Menu.title == 'dish_test_title1', Menu.description == 'dish_test_desc1') \
            .first()

        self.session.add(Submenu(title='dish_test_title1', description='dish_test_desc1', menu_id=self.menu1.id))
        self.session.commit()
        self.submenu1: Submenu = self.session.query(Submenu) \
            .filter_by(title='dish_test_title1', description='dish_test_desc1', menu_id=self.menu1.id) \
            .first()

        self.session.add(Dish(title='test_title1', description='test_desc1', price=12.34, submenu_id=self.submenu1.id))
        # session.add(Dish(title='test_title2', description='test_desc2', price=43.21, submenu_id=self.submenu1.id))
        self.session.commit()

        self.dish1: Dish = self.session.query(Dish) \
            .filter_by(title='test_title1', description='test_desc1', price=12.34, submenu_id=self.submenu1.id) \
            .first()

        self.data_for_create = dict(title='created_title', description='created_desc', price=522.1,
                                    submenu_id=str(self.submenu1.id))
        self.data_for_update = dict(title='updated_title', description='updated_desc', price=88.55)
        self.dishes_count = self.session.query(Dish).filter(Dish.submenu_id == self.submenu1.id).count()

    def test_get_dishes_ok(self, client, dish):
        response = client.get(f'/api/v1/menus/{self.menu1.id}/submenus/{self.submenu1.id}/dishes')
        dishes_from_response = [DishSchema(**dish) for dish in response.json()]
        dishes_from_db = [DishSchema(**as_dict(dish_data)) for dish_data in
                          dish.get_all(submenu_id=self.submenu1.id)]

        assert len(response.json()) == self.dishes_count
        assert response.status_code == 200
        assert dishes_from_response == dishes_from_db

    def test_get_dish_ok(self, client, dish):
        response = client.get(f'/api/v1/menus/{self.menu1.id}/submenus/{self.submenu1.id}/dishes/{self.dish1.id}')
        dish_from_response = DishSchema(**response.json())
        dish_from_db = DishSchema(**as_dict(dish.get_by_id(dish_id=self.dish1.id, submenu_id=self.submenu1.id)))

        assert response.status_code == 200
        assert dish_from_response == dish_from_db

    def test_create_dish_ok(self, client, dish):
        response = client.post(f'/api/v1/menus/{self.menu1.id}/submenus/{self.submenu1.id}/dishes',
                               json=self.data_for_create)
        dish_from_response = DishSchema(**response.json())
        self.created_dish_id = dish_from_response.id
        dish_from_db = DishSchema(**as_dict(dish.get_by_id(dish_id=self.created_dish_id,
                                                           submenu_id=self.submenu1.id)))

        assert len(dish.get_all(submenu_id=self.submenu1.id)) == self.dishes_count + 1
        assert response.status_code == 201
        assert dish_from_response == dish_from_db

    def test_update_dish_ok(self, client, dish):
        response = client.patch(f'/api/v1/menus/{self.menu1.id}/submenus/{self.submenu1.id}/dishes/{self.dish1.id}',
                                json=self.data_for_update)
        dish_from_response = DishSchema(**response.json())
        # self.session.refresh(self.submenu1)
        dish_from_db = DishSchema(**as_dict(dish.get_by_id(dish_id=self.dish1.id, submenu_id=self.submenu1.id)))

        assert response.status_code == 200
        assert dish_from_response == dish_from_db

    def test_delete_dish_ok(self, client, dish):
        response = client.delete(f'/api/v1/menus/{self.menu1.id}/submenus/{self.submenu1.id}/dishes/{self.dish1.id}')
        assert response.status_code == 200
        with pytest.raises(HTTPException) as ex:
            submenu_from_db = dish.get_by_id(dish_id=self.dish1.id, submenu_id=self.submenu1.id)

        assert ex.value.status_code == 404
        assert ex.value.detail == 'dish not found'

    def teardown_class(self):
        self.session.delete(self.menu1)
        self.session.delete(self.submenu1)
        self.session.delete(self.dish1)
        self.session.commit()
        self.session.close()
        print('teardown')
