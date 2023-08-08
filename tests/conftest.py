import pytest

from src.cache.client import redis_client
from src.config import get_mode
from src.db import engine
from src.menu_management.models import Base


@pytest.fixture(scope='session', autouse=True)
def setup_db():
    Base.metadata.drop_all(engine)
    assert get_mode() == 'TEST'
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    redis_client.flushall()
