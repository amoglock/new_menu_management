import pytest

from src.menu_management.schemas import CreateMenu
from src.menu_management.sevices.menu_service import MenuService


@pytest.fixture
def create_menu():
    MenuService.delete_all()
    menu = CreateMenu(title='my_menu', description='my_menu')
    MenuService.post_menu(menu)
    yield
    MenuService.delete_all()


@pytest.fixture
def get_menu_id():
    menu_id = MenuService.get_all_menu()[0]
    return str(menu_id.id)
