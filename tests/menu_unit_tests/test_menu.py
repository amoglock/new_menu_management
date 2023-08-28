from contextlib import nullcontext as does_not_raise

import pytest
from httpx import AsyncClient

from src.menu_management.sevices.menu_service import MenuService


class TestMenu:
    """
    Test class for async testing the menu router.
    """
    random_id = '5f4a67c2-832e-4975-b5cf-c3ed35015d98'
    invalid_id = '5f4a67c2-83'

    async def test_get_menu_list(self, ac: AsyncClient):
        """
        Test GET request for /api/v1/menus/

        :param ac: Async client from conftest.py
        :return: None

        Scenarios:
        - Empty base
        - After adding a menu instance

        Expected results:
        - Empty base: The response body should be an empty list. The status code should be 200.
        - After adding: The response body length should be equal to the numbers of menus in the base.
                        The status code should be 200.
                        The response body should be equal to the response model with right values.
        """
        response = await ac.get('/api/v1/menus/')
        assert response.json() == []
        assert response.status_code == 200

        await ac.post('/api/v1/menus/', json={
            'title': 'test_menu',
            'description': 'description'
        })
        response = await ac.get('/api/v1/menus/')
        assert response.status_code == 200
        assert len(response.json()) == await MenuService.count_menu()
        assert response.json() == [{'id': response.json()[0].get('id'), 'title': 'test_menu',
                                    'description': 'description', 'submenus_count': 0, 'dishes_count': 0}]

    @pytest.mark.parametrize(
        'title, description, expectation',
        [
            ('my_menu', 'my_menu_description', does_not_raise()),
            ('my_menu2', 'my_menu_description2', does_not_raise()),
        ]
    )
    async def test_post_correct_menu(self, ac: AsyncClient, title, description, expectation):
        """
        Test POST request for /api/v1/menus/ if request body is correct

        :param ac: Async client from conftest.py
        :param title: str title for new menu
        :param description: str description for new menu
        :param expectation: it is expected to be no raise errors. alias for nullcontext
        :return: None

        Scenarios:
        - Adds two menu instances

        Expected result after every step:
        - Status code equal 201.
        - The response body contains the fields: 'id', 'title', 'description', 'submenus_count', 'dishes_count'.
        - The 'id' field is str type.
        - The 'submenus_count' field is int type.
        - The 'dishes_count' field is int type.
        - The 'title' field is correct and contains the passed value.
        - The 'description' field is correct and contains the passed value.
        """
        with expectation:
            response = await ac.post('/api/v1/menus/', json={
                'title': title,
                'description': description
            })
            assert response.status_code == 201
            assert all(['id', 'title', 'description', 'submenus_count', 'dishes_count' in response.json()])
            assert isinstance(response.json().get('id'), str)
            assert isinstance(response.json().get('submenus_count'), int)
            assert isinstance(response.json().get('dishes_count'), int)
            assert response.json().get('title') == title
            assert response.json().get('description') == description

    @pytest.mark.parametrize(
        'title, description, status_code, expectation',
        [
            (112454, 'my_menu with non_string title', 422, does_not_raise()),
            ('menu with non string desc.', 12.254, 422, does_not_raise()),
        ]
    )
    async def test_post_incorrect_menu(self, ac: AsyncClient, title, description, status_code, expectation):
        """
        Test POST request for /api/v1/menus/ if request body is not correct

        :param ac: Async client from conftest.py
        :param title: str title for new menu
        :param description: str description for new menu
        :param status_code: expected status code
        :param expectation: it is expected to be no raise errors. alias for nullcontext
        :return: None

        Scenarios:
        - Title is not string
        - Description is not string

        Expected result:
        - The response status code equal 422.
        """
        with expectation:
            response = await ac.post('/api/v1/menus/', json={
                'title': title,
                'description': description
            })
            assert response.status_code == status_code

    async def test_menu_already_exists(self, ac: AsyncClient):
        """
        Test POST request for /api/v1/menus/ if the menu title already exist in the base

        :param ac: Async client from conftest.py
        :return: None

        Scenario:
        - Adds new menu with 'my_menu' title. This title is already in the database

        Expected result:
        - The response status code equal 409.
        - The response body equal {'detail': 'This menu title already exists'}
        """
        response = await ac.post('/api/v1/menus/', json={
            'title': 'my_menu',
            'description': 'my_menu_description'
        })
        assert response.status_code == 409
        assert response.json() == {'detail': 'This menu title already exists'}

    async def test_get_specific_menu(self, ac: AsyncClient):
        """
        Test POST request for /api/v1/menus/menu_id

        :param ac: Async client from conftest.py
        :return: None

        Scenario:
        - Add new menu and try to get the menu by id
        - Correct id
        - Correct id but not exists in the database
        - Incorrect id type

        Expected result:
        - Correct id: The response status code equal 200. The response body contains correct menu instance.
        - Correct id but not exists in the database: The response status code equal 404.
            The response body equal {'detail': 'menu not found'}.
        - Incorrect id type: The response status code equal 404. The response body equal {'detail': error message}.
        """
        response = await ac.post('/api/v1/menus/', json={
            'title': 'specific_menu',
            'description': 'specific_menu_description'
        })
        specific_menu = response.json()
        response = await ac.get(f"api/v1/menus/{specific_menu.get('id')}")
        assert response.status_code == 200
        assert response.json() == specific_menu
        response = await ac.get(f'api/v1/menus/{self.random_id}')
        assert response.status_code == 404
        assert response.json() == {'detail': 'menu not found'}
        response = await ac.get(f'api/v1/menus/{self.invalid_id}')
        assert response.status_code == 404
        assert response.json() == {
            'detail': f"<class 'asyncpg.exceptions.DataError'>: invalid input for query argument $1:"
                      f" '{self.invalid_id}' (invalid UUID '{self.invalid_id}': length must be between 32..36"
                      f' characters, got 11)'}

    async def test_patch_menu(self, ac: AsyncClient):
        """
        Test PATCH request for /api/v1/menus/menu_id

        :param ac: Async client from conftest.py
        :return: None

        Scenarios:
        - Add new menu
        - Patch the new menu
        - Patch a non-existent menu
        - Send the wrong 'title' type
        - Send the wrong 'description' type

        Expected results:
        - Patch the new menu: The response status code equal 200. The response 'id' field not changed.
            The response 'id' field not changed. The response 'title' field has new value.
            The response 'description' field has new value.
        - Patch a non-existent menu: The response status code equal 404.
            The response body equal {'detail': 'menu not found'}
        - Send the wrong 'title' type: The response status code equal 422.
        - Send the wrong 'description' type: The response status code equal 422.
        """
        response = await ac.post('/api/v1/menus/', json={
            'title': 'menu_for_update',
            'description': 'menu_for_update_description'
        })
        menu_for_update = response.json()
        response = await ac.patch(f"api/v1/menus/{menu_for_update.get('id')}", json={
            'title': 'patched_menu',
            'description': 'patched_description'
        })
        assert response.status_code == 200
        assert response.json().get('id') == menu_for_update.get('id')
        assert response.json().get('title') == 'patched_menu'
        assert response.json().get('description') == 'patched_description'
        response = await ac.patch(f'api/v1/menus/{self.random_id}', json={
            'title': 'menu_for_update',
            'description': 'menu_for_update_description'
        })
        assert response.status_code == 404
        assert response.json() == {'detail': 'menu not found'}
        response = await ac.patch(f"api/v1/menus/{menu_for_update.get('id')}", json={
            'title': 123,
            'description': 'menu_for_update_description'
        })
        assert response.status_code == 422
        response = await ac.patch(f"api/v1/menus/{menu_for_update.get('id')}", json={
            'title': 'patched_menu',
            'description': 12345
        })
        assert response.status_code == 422

    async def test_delete_menu(self, ac: AsyncClient):
        """
        Test DELETE request for /api/v1/menus/menu_id

        :param ac: Async client from conftest.py
        :return: None

        Scenarios:
        - Add new menu
        - Delete the new menu
        - Delete the new menu second time
        - Delete a non-existent menu
        - Delete a menu by wrong menu_id type

        Expected results:
        - Delete the new menu: The response status code equal 200.
            The response body equal {'status': True, 'message': 'menu has been deleted'}.
        - Delete the new menu second time: The response status code equal 200.
            The response body equal {'status': False, 'message': 'menu not found'}.
        - Delete a non-existent menu: The response status code equal 200.
            The response body equal {'status': False, 'message': 'menu not found'}.
        - Delete a menu by wrong menu_id type: The response status code equal 404.
            The response body equal {'detail': error message}.
        """
        menu_for_delete = await ac.post('/api/v1/menus/', json={
            'title': 'menu_for_delete',
            'description': 'menu_for_delete_description'
        })
        response = await ac.delete(f"api/v1/menus/{menu_for_delete.json().get('id')}")
        assert response.status_code == 200
        assert response.json() == {'status': True, 'message': 'menu has been deleted'}
        response = await ac.delete(f"api/v1/menus/{menu_for_delete.json().get('id')}")
        assert response.status_code == 200
        assert response.json() == {'status': False, 'message': 'menu not found'}
        response = await ac.delete(f'api/v1/menus/{self.random_id}')
        assert response.status_code == 200
        assert response.json() == {'status': False, 'message': 'menu not found'}
        response = await ac.delete(f'api/v1/menus/{self.invalid_id}')
        assert response.status_code == 404
        assert response.json() == {
            'detail': f"<class 'asyncpg.exceptions.DataError'>: invalid input for query argument $1:"
                      f" '{self.invalid_id}' (invalid UUID '{self.invalid_id}': length must be between 32..36 "
                      f'characters, got 11)'}
