import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine

from src.config import settings
from src.main import app
from src.menu_management.models import Base

DATABASE_URL_TEST = settings.db_url
engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)


@pytest.fixture(scope='session', autouse=True)
async def setup_db() -> AsyncGenerator:
    """
    Creates tables before tests and drop all tables after tests done

    :return: AsyncGenerator
    """
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def clear_db() -> None:
    """
    Drops the database and create clear database

    :return: None
    """
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def ac() -> AsyncGenerator[AsyncClient, None]:
    """
    Async client for tests

    :return: AsyncClient
    """
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


@pytest.fixture(scope='session')
async def get_menu_id(ac: AsyncClient) -> str:
    """
    Returns menu_id from not empty database for use in tests

    :param ac: Async client
    :return: str menu_id for fist menu in list
    """
    response = await ac.get('/api/v1/menus/')
    menu_id = response.json()[0].get('id')
    return menu_id


@pytest.fixture(scope='session')
async def get_submenu_id(ac: AsyncClient) -> str:
    """
    Returns submenu_id from not empty database for use in tests

    :param ac: Async client
    :return: str submenu_id for fist submenu in list
    """
    response = await ac.get('/api/v1/menus/')
    menu_id = response.json()[0].get('id')
    response = await ac.get(f'/api/v1/menus/{menu_id}/submenus/')
    submenu_id = response.json()[0].get('id')
    return submenu_id
