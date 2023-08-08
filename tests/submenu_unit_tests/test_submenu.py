from contextlib import nullcontext as does_not_raise

import pytest
from pydantic_core import ValidationError

from src.cache.client import redis_client
from src.menu_management.schemas import CreateSubmenu, PatchSubmenu, SubmenuResponse
from src.menu_management.sevices.submenu_servise import SubmenuService


@pytest.mark.usefixtures('create_menu')
class TestSubmenu:
    def test_get_all_submenu_empty_base(self, get_menu_id):
        """Checks response is empty list with empty base"""

        redis_client.delete('all_submenu')
        res = SubmenuService.get_all_submenus(get_menu_id)

        assert res == []

    @pytest.mark.parametrize(
        'title, description, expectation',
        [
            ('my_submenu', 'my_submenu_description', does_not_raise()),
            ('my_submenu2', 'my_submenu_description2', does_not_raise()),
            (112454, 'my_submenu with non_string title', pytest.raises(ValidationError)),
            ('submenu with non string desc.', 12.254, pytest.raises(ValidationError)),
        ]
    )
    def test_post_submenu(self, title, description, expectation, get_menu_id):
        """
        Checks add is success and count table should be plus one. Checks validation. All model`s fields must be string
        """

        assert SubmenuService.count() == 0
        with expectation:
            SubmenuService.post_submenu(get_menu_id, CreateSubmenu(title=title, description=description))
            assert SubmenuService.count() == 1

    def test_get_all_submenu(self, get_menu_id):
        """Checks response is List and follow to check added submenu is match with menus list"""

        submenus = [
            CreateSubmenu(title='my_submenu', description='my_submenu'),
            CreateSubmenu(title='my_submenu2', description='my_submenu2'),
        ]

        for submenu in submenus:
            SubmenuService.post_submenu(get_menu_id, submenu)
            res = SubmenuService.get_all_submenus(get_menu_id)
            assert isinstance(res, list)
            for r in res:
                assert isinstance(r, SubmenuResponse)
                assert CreateSubmenu(**r.model_dump()) in submenus

    def test_get_specific_submenu(self, get_menu_id):
        """Checks correct response for request submenu by id. Checks response get_submenu() is SubmenuResp. instance"""

        submenu = CreateSubmenu(title='my_submenu', description='my_submenu')
        added_submenu = SubmenuService.post_submenu(get_menu_id, submenu)
        assert isinstance(added_submenu, SubmenuResponse)
        assert SubmenuService.get_submenu(str(added_submenu.id)) == added_submenu.model_dump()

    def test_patch_submenu(self, get_menu_id):
        """Checks correct patched submenu"""

        submenu = CreateSubmenu(title='my_submenu', description='my_submenu')
        correct_for_submenu = PatchSubmenu(title='my_corrected_submenu', description='my_corrected_submenu')
        new_submenu = SubmenuService.post_submenu(get_menu_id, submenu)
        corrected_menu = SubmenuService.patch_submenu(str(new_submenu.id), correct_for_submenu)
        assert corrected_menu.get('title') == correct_for_submenu.title
        assert corrected_menu.get('description') == correct_for_submenu.description

    def test_delete_menu(self, get_menu_id):
        """Checks deleting is correct"""
        submenu = CreateSubmenu(title='my_submenu', description='my_submenu')
        added_menu = SubmenuService.post_submenu(get_menu_id, submenu)
        assert SubmenuService.count() == 1
        SubmenuService.delete(str(added_menu.id))
        assert SubmenuService.count() == 0
