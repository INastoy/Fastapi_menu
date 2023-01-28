import pytest
from starlette.testclient import TestClient

from apps.menu.crud import MenuCRUD, SubmenuCRUD, DishCRUD
from core.database import Session
from main import app


@pytest.fixture(scope='module')
def client():
    # app.dependency_overrides[get_session] = override_get_session
    client = TestClient(app)
    yield client


@pytest.fixture(scope='module')
def session():
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope='module')
def menu(session):
    menu = MenuCRUD(session=session)
    yield menu


@pytest.fixture(scope='module')
def submenu(session):
    submenu = SubmenuCRUD(session=session)
    yield submenu


@pytest.fixture(scope='module')
def dish(session):
    dish = DishCRUD(session=session)
    yield dish
