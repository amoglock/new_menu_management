from contextlib import nullcontext as does_not_raise

import pytest
from httpx import AsyncClient

from src.menu_management.sevices.dish_service import DishService


class TestDish:
    random_id = '5f4a67c2-832e-4975-b5cf-c3ed35015d98'
    invalid_id = '5f4a67c2-83'

    async def test_get_dishes_list(self, ac: AsyncClient, get_menu_id, get_submenu_id) -> None:
        """
        Test GET request for '/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/'

        :param ac: Async client from conftest.py
        :param get_menu_id: str menu_id from fixture
        :param get_submenu_id: str submenu_id from fixture
        :return: None

        Scenarios:
        - Empty base
        - After adding a dish instance
        - Invalid submenu_id

        Expected results:
        - Empty base: The response body equal empty list. The response status code equal 200.
        - After adding a dish instance: The response body length should be equal to the numbers of dishes
            in the base. The status code should be 200. The response body should be equal to the response
            model with right values.
        - Invalid submenu_id: The response status code should be 404. The response body equal {'detail': error message}
        """
        response = await ac.get(f'/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/')
        assert response.json() == []
        assert response.status_code == 200

        await ac.post(f'/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/', json={
            'title': 'test_dish',
            'description': 'description',
            'price': '52.3'
        })
        response = await ac.get(f'/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/')
        assert response.status_code == 200
        assert len(response.json()) == await DishService.count()
        assert response.json() == [{'id': response.json()[0].get('id'), 'title': 'test_dish',
                                    'description': 'description', 'price': '52.30'}]
        response = await ac.get(f'/api/v1/menus/{get_menu_id}/submenus/{self.invalid_id}/dishes/')
        assert response.status_code == 404
        assert response.json() == {'detail': f"<class 'asyncpg.exceptions.DataError'>: invalid input for query argument"
                                             f" $1: '{self.invalid_id}' (invalid UUID '{self.invalid_id}': "
                                             f'length must be between 32..36 characters, got 11)'}

    @pytest.mark.parametrize(
        'title, description, price, expectation',
        [
            ('my_dish', 'my_dish_description', '52.6', does_not_raise()),
            ('my_dish2', 'my_dish_description2', '12.12548', does_not_raise()),
        ]
    )
    async def test_post_correct_dish(
            self, ac: AsyncClient, title, description, price, expectation, get_menu_id, get_submenu_id) -> None:
        """
        Test POST request for '/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/'

        :param title: str dish title
        :param description: str dish description
        :param expectation: it is expected to be no raise errors. alias for nullcontext
        :param price: str dish price
        :param get_menu_id: str menu_id from fixture
        :param get_submenu_id: str submenu_id from fixture
        :return: none

        Scenarios:
        - Adds two dish instances

        Expected result after every step:
        - Status code equal 201.
        - The response body contains the fields: 'id', 'title', 'price'.
        - The 'id' field is str type.
        - The 'price' field is str type and contains two decimal places.
        - The 'title' field is correct and contains the passed value.
        - The 'description' field is correct and contains the passed value.

        """
        with expectation:
            response = await ac.post(f'/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/', json={
                'title': title,
                'description': description,
                'price': price
            })
            assert response.status_code == 201
            assert all(['id', 'title', 'price' in response.json()])
            assert isinstance(response.json().get('id'), str)
            assert isinstance(response.json().get('price'), str)
            assert len(response.json().get('price').split('.')[1]) == 2
            assert response.json().get('title') == title
            assert response.json().get('description') == description

    @pytest.mark.parametrize(
        'title, description, price, status_code, expectation',
        [
            (112454, 'dish with non_string title', '12', 422, does_not_raise()),
            ('dish with non string desc.', 12.254, '12', 422, does_not_raise()),
            ('dish with non string price', 'dish desc.', 12, 422, does_not_raise()),
        ]
    )
    async def test_post_incorrect_dish(
            self, ac: AsyncClient, title, description, price, status_code, expectation, get_menu_id, get_submenu_id):
        """
        Test POST request for '/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/' if request body is not correct

        :param ac: Async client from conftest.py
        :param title: str dish title
        :param description: str dish description
        :param price: str dish price
        :param expectation: it is expected to be no raise errors. alias for nullcontext
        :param get_menu_id: str menu_id from fixture
        :param get_submenu_id: str submenu_id from fixture
        :return: None

        Scenarios:
        - Wrong type title
        - Wrong type description
        - Wrong type price

        Expected result:
        - The response status code equal 422.
        """
        with expectation:
            response = await ac.post(f'/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/', json={
                'title': title,
                'description': description,
                'price': price
            })
            assert response.status_code == status_code

    async def test_get_dish_by_id(self, ac: AsyncClient, get_menu_id, get_submenu_id) -> None:
        """
        Test POST request for '/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}'

        :param ac: Async client from fixture
        :param get_submenu_id: str submenu_id from fixture
        :return: None

        Scenarios:
        - Add a new dish
        - Correct id
        - Correct id but not exists in the database
        - Incorrect id type

        Expected results:
        - Correct id: The response status code equal 200. The response body is correct.
        - Correct id but not exists in the database: the response status code equal 404.
            The response body equal {'detail': 'dish not found'}.
        - Incorrect id type: the response status code equal 404.
            The response body equal {'detail': error message}.
        """
        response = await ac.post(f'/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/', json={
            'title': 'specific_dish',
            'description': 'description',
            'price': '52.3'
        })
        specific_dish = response.json()
        response = await ac.get(
            f'/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/{specific_dish.get("id")}')
        assert response.status_code == 200
        assert response.json() == specific_dish
        response = await ac.get(f'/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/{self.random_id}')
        assert response.status_code == 404
        assert response.json() == {'detail': 'dish not found'}
        response = await ac.get(f'/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/{self.invalid_id}')
        assert response.status_code == 404
        assert response.json() == {'detail': f"<class 'asyncpg.exceptions.DataError'>: invalid input for query argument"
                                             f" $1: '{self.invalid_id}' (invalid UUID '{self.invalid_id}': "
                                             f'length must be between 32..36 characters, got 11)'}

    async def test_update_dish(self, ac: AsyncClient, get_menu_id, get_submenu_id) -> None:
        """
        Test PATCH request for '/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}'

        :param ac: Async client from conftest.py
        :param get_menu_id: str menu_id from fixture
        :return: None

        Scenarios:
        - Add new dish
        - Patch the new dish
        - Patch a non-existent dish
        - Send the wrong 'title' type
        - Send the wrong 'description' type
        - Send the wrong 'price' type

        Expected results:
        - Patch the new dish: The response status code equal 200. The response 'id' field not changed.
            The response 'title' field has new value. The response 'description' field has new value.
            The response 'price' field has new value.
        - Patch a non-existent dish: The response status code equal 200.
            The response body equal {'detail': 'dish not found'}
        - Send the wrong 'title' type: The response status code equal 422.
        - Send the wrong 'description' type: The response status code equal 422.
        - Send the wrong 'price' type: The response status code equal 422.
        """
        response = await ac.post(f'/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/', json={
            'title': 'dish_for_patch',
            'description': 'description_for_patch',
            'price': '12.345'
        })
        dish_for_update = response.json()
        response = await ac.patch(
            f'/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/{dish_for_update.get("id")}', json={
                'title': 'patched_dish',
                'description': 'patched_description',
                'price': '54.321'
            })
        assert response.status_code == 200
        assert response.json().get('id') == dish_for_update.get('id')
        assert response.json().get('title') == 'patched_dish'
        assert response.json().get('description') == 'patched_description'
        assert response.json().get('price') == '54.32'
        response = await ac.patch(
            f'/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/{self.random_id}', json={
                'title': 'patched_dish',
                'description': 'patched_description',
                'price': '54.321'
            })
        assert response.status_code == 404
        assert response.json() == {'detail': 'dish not found'}
        response = await ac.patch(
            f'/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/{dish_for_update.get("id")}', json={
                'title': 23,
                'description': 'patched_description',
                'price': '54.321'
            })
        assert response.status_code == 422
        response = await ac.patch(
            f'/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/{dish_for_update.get("id")}', json={
                'title': 'correct',
                'description': 23,
                'price': '54.321'
            })
        assert response.status_code == 422
        response = await ac.patch(
            f'/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/{dish_for_update.get("id")}', json={
                'title': 'correct',
                'description': 'patched_description',
                'price': 54.321
            })
        assert response.status_code == 422

    async def test_delete_dish(self, ac: AsyncClient, get_menu_id, get_submenu_id) -> None:
        """
        Test DELETE request for '/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}'

        :param ac: Async client from conftest.py
        :param get_menu_id: str menu_id from fixture
        :param get_submenu_id: str submenu_id from fixture
        :return: None

        Scenarios:
        - Add new dish
        - Delete the new dish
        - Delete the new dish second time
        - Delete a non-existent dish
        - Delete a dish by wrong dish_id type

        Expected results:
        - Delete the new dish: The response status code equal 200.
            The response body equal {'status': True, 'message': 'The dish has been deleted'}.
        - Delete the new dish second time: The response status code equal 200.
            The response body equal {'status': False, 'message': 'The dish not found'}.
        - Delete a non-existent dish: The response status code equal 200.
            The response body equal {'status': False, 'message': 'The dish not found'}.
        - Delete a dish by wrong dish_id type: The response status code equal 404.
            The response body equal {'detail': error message}.
        """
        dish_for_delete = await ac.post(f'/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/', json={
            'title': 'dish_for_delete',
            'description': 'description_for_delete',
            'price': '12.345'
        })
        response = await ac.delete(
            f'/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/{dish_for_delete.json().get("id")}')
        assert response.status_code == 200
        assert response.json() == {'status': True, 'message': 'The dish has been deleted'}
        response = await ac.delete(
            f'/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/{dish_for_delete.json().get("id")}')
        assert response.status_code == 200
        assert response.json() == {'status': False, 'message': 'The dish not found'}
        response = await ac.delete(f'/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/{self.random_id}')
        assert response.status_code == 200
        assert response.json() == {'status': False, 'message': 'The dish not found'}
        response = await ac.delete(f'/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/{self.invalid_id}')
        assert response.status_code == 404
        assert response.json() == {
            'detail': f"<class 'asyncpg.exceptions.DataError'>: invalid input for query argument $1:"
                      f" '{self.invalid_id}' (invalid UUID '{self.invalid_id}': length must be between 32..36 "
                      f'characters, got 11)'}
