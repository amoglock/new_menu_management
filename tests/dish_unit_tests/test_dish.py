from contextlib import nullcontext as does_not_raise

import pytest
from pydantic_core import ValidationError

from src.menu_management.schemas import CreateDish, DishResponse, PatchDish
from src.menu_management.sevices.dish_service import DishService
from src.menu_management.sevices.submenu_servise import SubmenuService


@pytest.mark.usefixtures('create_menu_submenu')
class TestDish:
    def test_get_all_dishes_empty_base(self, get_submenu_id):
        """Checks response is empty list with empty base"""

        res = DishService.get_all_dishes(get_submenu_id)

        assert res == []

    @pytest.mark.parametrize(
        'title, description, price, expectation',
        [
            ('my_dish', 'my_dish_description', '52.6', does_not_raise()),
            ('my_dish2', 'my_dish_description2', '12.12548', does_not_raise()),
            (112454, 'dish with non_string title', '12', pytest.raises(ValidationError)),
            ('dish with non string desc.', 12.254, '12', pytest.raises(ValidationError)),
            ('dish with non string price', 'dish desc.', 12, pytest.raises(ValidationError)),
        ]
    )
    def test_post_dish(self, title, description, expectation, price, get_submenu_id):
        """
        Checks add is success and count table should be plus one. Checks validation. All model`s fields must be string
        """

        assert DishService.count() == 0
        with expectation:
            DishService.post_dish(get_submenu_id, CreateDish(title=title, description=description, price=price))
            assert SubmenuService.count() == 1

    def test_get_all_dishes(self, get_submenu_id):
        """Checks response is List and follow to check added submenu is match with menus list"""

        dishes = [
            CreateDish(title='my_dish', description='my_dish', price='15.23654'),
            CreateDish(title='my_dish2', description='my_dish2', price='15.23654'),
        ]

        for dish in dishes:
            DishService.post_dish(get_submenu_id, dish)
            res = DishService.get_all_dishes(get_submenu_id)
            assert isinstance(res, list)
            for r in res:
                assert isinstance(r, DishResponse)

    def test_get_specific_dish(self, get_submenu_id):
        """Checks correct response for request dish by id. Checks response get_dish() is DishResp. instance"""

        dish = CreateDish(title='my_submenu', description='my_submenu', price='12.3456')
        added_dish = DishService.post_dish(get_submenu_id, dish)
        assert isinstance(added_dish, DishResponse)
        assert DishService.get_dish(str(added_dish.id)) == added_dish.model_dump()

    def test_patch_dish(self, get_submenu_id):
        """Checks correct patched dish"""

        dish = CreateDish(title='my_submenu', description='my_submenu', price='15.2')
        correct_for_dish = PatchDish(title='my_corrected_dish', description='my_corrected_dish', price='16')
        new_dish = DishService.post_dish(get_submenu_id, dish)
        corrected_dish = DishService.patch_dish(str(new_dish.id), correct_for_dish)
        assert corrected_dish.get('title') == correct_for_dish.title
        assert corrected_dish.get('description') == correct_for_dish.description
        assert len(corrected_dish.get('price')) == 5

    def test_delete_dish(self, get_submenu_id):
        """Checks deleting is correct"""

        dish = CreateDish(title='my_dish', description='my_dish', price='12.34')
        added_dish = DishService.post_dish(get_submenu_id, dish)
        assert DishService.count() == 1
        DishService.delete(str(added_dish.id))
        assert DishService.count() == 0
