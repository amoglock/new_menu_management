from contextlib import nullcontext as does_not_raise

import pytest
from pydantic_core import ValidationError

from src.menu_management.schemas import CreateMenu, MenuResponse, PatchMenu
from src.menu_management.sevices.menu_service import MenuService


@pytest.mark.usefixtures('empty_menu_table')
class TestMenu:

    def test_get_all_menu_empty_base(self):
        """Checks response is empty list with empty base"""

        res = MenuService.get_all_menu()

        assert res == []

    @pytest.mark.parametrize(
        'title, description, expectation',
        [
            ('my_menu', 'my_menu_description', does_not_raise()),
            ('my_menu2', 'my_menu_description2', does_not_raise()),
            (112454, 'my_menu with non_string title', pytest.raises(ValidationError)),
            ('menu with non string desc.', 12.254, pytest.raises(ValidationError)),
        ]
    )
    def test_post_menu(self, title, description, expectation):
        """
        Checks add is success and count table should be plus one. Checks validation. All model`s fields must be string
        """

        assert MenuService.count() == 0
        with expectation:
            MenuService.post_menu(CreateMenu(title=title, description=description))
            assert MenuService.count() == 1

    def test_get_all_menu(self):
        """Checks response is List and follow to check added menu is match with menus list"""

        menus = [
            CreateMenu(title='my_menu', description='my_menu'),
            CreateMenu(title='my_menu2', description='my_menu2'),
        ]

        for menu in menus:
            MenuService.post_menu(menu)
            res = MenuService.get_all_menu()
            assert isinstance(res, list)
            for r in res:
                assert isinstance(r, MenuResponse)
                assert CreateMenu(**r.model_dump()) in menus

    def test_get_specific_menu(self):
        """Checks correct response for request menu by id. Checks response get_menu() is dict instance"""

        menu = CreateMenu(title='my_menu', description='my_menu')
        added_menu = MenuService.post_menu(menu)
        assert isinstance(MenuService.get_menu(str(added_menu.id)), MenuResponse)
        assert MenuService.get_menu(str(added_menu.id)) == added_menu

    def test_patch_menu(self):
        """Checks correct patched menu"""

        menu = CreateMenu(title='my_menu', description='my_menu')
        correct_for_menu = PatchMenu(title='my_corrected_menu', description='my_corrected_menu')
        new_menu = MenuService.post_menu(menu)
        corrected_menu = MenuService.patch_menu(str(new_menu.id), correct_for_menu)
        assert corrected_menu.get('title') == correct_for_menu.title
        assert corrected_menu.get('description') == correct_for_menu.description

    def test_delete_menu(self):
        """Checks deleting is correct"""

        menu = CreateMenu(title='my_menu', description='my_menu')
        added_menu = MenuService.post_menu(menu)
        assert MenuService.count() == 1
        MenuService.delete(str(added_menu.id))
        assert MenuService.count() == 0
