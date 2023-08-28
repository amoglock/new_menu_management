import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine

from src.config import db_url
from src.main import app
from src.menu_management.models import Base

DATABASE_URL_TEST = db_url()
engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)


@pytest.fixture(scope='session', autouse=True)
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


@pytest.fixture
async def get_menu_id(ac: AsyncClient) -> str:
    response = await ac.get('/api/v1/menus/')
    menu_id = response.json()[0].get('id')
    return menu_id
