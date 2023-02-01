import asyncio
from typing import Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from apps.menu.crud import MenuCRUD, SubmenuCRUD, DishCRUD
from core.database import Session
from main import app


@pytest.fixture(scope='session')
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='module')
async def client():
    # app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(app=app, base_url='http://test') as async_client:
        yield async_client
    # client = TestClient(app)
    # yield client


@pytest_asyncio.fixture(scope='module')
async def session() -> AsyncSession:
    async_session = Session()
    async with async_session as session:
        yield session
# def session():
#     session = Session()
#     try:
#         yield session
#     finally:
#         session.close()


@pytest_asyncio.fixture(scope='module')
async def menu(session):
    menu = MenuCRUD(session=session)
    yield menu


@pytest_asyncio.fixture(scope='module')
async def submenu(session):
    submenu = SubmenuCRUD(session=session)
    yield submenu


@pytest_asyncio.fixture(scope='module')
async def dish(session):
    dish = DishCRUD(session=session)
    yield dish

# async def init_models():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
