import pytest

from src.menu_management.sevices.menu_service import MenuService


@pytest.fixture
def empty_menu_table():
    MenuService.delete_all()
