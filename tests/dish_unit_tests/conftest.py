import pytest

from src.menu_management.schemas import CreateMenu, CreateSubmenu
from src.menu_management.sevices.menu_service import MenuService
from src.menu_management.sevices.submenu_servise import SubmenuService


@pytest.fixture
def create_menu_submenu():
    MenuService.delete_all()
    menu = CreateMenu(title="my_menu", description="my_menu")
    submenu = CreateSubmenu(title="my_submenu", description="my_submenu")
    MenuService.post_menu(menu)
    menu_id = str(MenuService.get_all_menu()[0].id)
    SubmenuService.post_submenu(menu_id, submenu)
    yield
    MenuService.delete_all()


@pytest.fixture
def get_submenu_id():
    menu_id = str(MenuService.get_all_menu()[0].id)
    submenu_id = str(SubmenuService.get_all_submenus(menu_id)[0].id)
    return submenu_id
