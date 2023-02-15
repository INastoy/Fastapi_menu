import asyncio
import platform
from typing import Generator

import asyncpg
import pytest
import pytest_asyncio
from asyncpg import ConnectionDoesNotExistError, InvalidCatalogNameError
from httpx import AsyncClient
from redis.asyncio.client import Redis  # type: ignore
from redis.asyncio.connection import ConnectionPool  # type: ignore
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from apps.menu.crud import DishCRUD, MenuCRUD, SubmenuCRUD
from core.cache.redis import get_cache_client
from core.database import Base, get_session
from core.settings import (
    CACHE_DB_NUM,
    CACHE_URL,
    DATABASE_PASSWORD,
    DATABASE_URL,
    DATABASE_USER,
    TEST_CACHE_DB_NUM,
    TEST_DB_NAME,
)
from main import fastapi_app

DATABASE_NAME = DATABASE_URL.split('/')[-1]  # type: ignore
test_db_url = DATABASE_URL.replace(DATABASE_NAME, TEST_DB_NAME)  # type: ignore
test_engine: AsyncEngine = create_async_engine(test_db_url)
t_session = sessionmaker(test_engine, class_=AsyncSession)


async def get_test_session() -> AsyncSession:

    async with t_session() as async_session:
        yield async_session


async def get_test_cache_client():
    test_cache_url = CACHE_URL.replace(CACHE_DB_NUM, TEST_CACHE_DB_NUM)
    connection_pool = ConnectionPool.from_url(url=test_cache_url)
    async_cache_client = Redis(connection_pool=connection_pool)
    async with async_cache_client as cache_client:
        yield cache_client


async def create_db_if_not_exists():
    try:
        async with test_engine.begin():
            pass
    except (ConnectionDoesNotExistError, InvalidCatalogNameError):
        sys_conn = await asyncpg.connect(
            database='postgres',
            user=DATABASE_USER,
            password=DATABASE_PASSWORD
        )
        await sys_conn.execute(
            f'CREATE DATABASE "{TEST_DB_NAME}" OWNER "{DATABASE_USER}"'
        )
        await sys_conn.close()
    await test_engine.dispose()


@pytest.fixture(scope='session')
def event_loop() -> Generator:
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def client():
    fastapi_app.dependency_overrides[get_session] = get_test_session
    fastapi_app.dependency_overrides[get_cache_client] = get_test_cache_client
    async with AsyncClient(app=fastapi_app, base_url='http://test') as async_client:
        yield async_client

    fastapi_app.dependency_overrides = {}


@pytest_asyncio.fixture(scope='session')
async def session() -> AsyncSession:
    await create_db_if_not_exists()
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with t_session() as async_session:
        yield async_session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope='module')
async def menu(session):
    menu_crud = MenuCRUD(session=session)
    yield menu_crud


@pytest_asyncio.fixture(scope='module')
async def submenu(session):
    submenu_crud = SubmenuCRUD(session=session)
    yield submenu_crud


@pytest_asyncio.fixture(scope='module')
async def dish(session):
    dish_crud = DishCRUD(session=session)
    yield dish_crud


# async def init_models():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
