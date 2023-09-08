from contextlib import nullcontext as does_not_raise

import pytest
from httpx import AsyncClient


class TestSubmenu:
    random_id = '5f4a67c2-832e-4975-b5cf-c3ed35015d98'
    invalid_id = '5f4a67c2-83'

    async def test_get_submenus_list(self, ac: AsyncClient, get_menu_id) -> None:
        """
        Test GET request for api/v1/menus/{menu_id}/submenus/

        :param ac: Async client from conftest.py
        :param get_menu_id: str menu_id from fixture
        :return: None

        Scenario:
        - Empty submenu base
        - After adding a submenu instance
        - Invalid menu_id

        Expected result:
        - Empty submenu base: The response body equal empty list. The response status code equal 200.
        - After adding a submenu instance: The response body length should be equal to the numbers of submenus
            in the base. The status code should be 200. The response body should be equal to the response
            model with right values.
        - Invalid menu_id: The response status code should be 200. The response body equal {'detail': error message}
        """
        response = await ac.get(f'/api/v1/menus/{get_menu_id}/submenus/')
        assert response.status_code == 200
        assert response.json() == []

        await ac.post(f'/api/v1/menus/{get_menu_id}/submenus/', json={
            'title': 'test_submenu',
            'description': 'description'
        })
        response = await ac.get(f'/api/v1/menus/{get_menu_id}/submenus/')
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json() == [{'id': response.json()[0].get('id'), 'title': 'test_submenu',
                                    'description': 'description', 'dishes_count': 0}]

        response = await ac.get(f'/api/v1/menus/{self.invalid_id}/submenus/')
        assert response.status_code == 404
        assert response.json() == {'detail': f"<class 'asyncpg.exceptions.DataError'>: invalid input for query argument"
                                             f" $1: '{self.invalid_id}' (invalid UUID '{self.invalid_id}':"
                                             f' length must be between 32..36 characters, got 11)'}

    @pytest.mark.parametrize(
        'title, description, expectation',
        [
            ('my_submenu', 'my_submenu_description', does_not_raise()),
            ('my_submenu2', 'my_submenu_description2', does_not_raise()),
        ]
    )
    async def test_post_correct_submenu(self, ac: AsyncClient, title, description, expectation, get_menu_id) -> None:
        """
        Test POST request for api/v1/menus/{menu_id}/submenus/

        :param title: str title submenu
        :param description: str description submenu
        :param expectation: it is expected to be no raise errors. alias for nullcontext
        :param get_menu_id: str menu_id from fixture
        :return: None

        Scenarios:
        - Adds two submenu instances

        Expected result after every step:
        - Status code equal 201.
        - The response body contains the fields: 'id', 'title', 'description', 'dishes_count'.
        - The 'id' field is str type.
        - The 'dishes_count' field is int type.
        - The 'title' field is correct and contains the passed value.
        - The 'description' field is correct and contains the passed value.
        """
        with expectation:
            response = await ac.post(f'/api/v1/menus/{get_menu_id}/submenus/', json={
                'title': title,
                'description': description
            })
            assert response.status_code == 201
            assert all(['id', 'title', 'description', 'dishes_count' in response.json()])
            assert isinstance(response.json().get('id'), str)
            assert isinstance(response.json().get('dishes_count'), int)
            assert response.json().get('title') == title
            assert response.json().get('description') == description

    @pytest.mark.parametrize(
        'title, description, status_code, expectation',
        [
            (112454, 'my_submenu with non_string title', 422, does_not_raise()),
            ('submenu with non string desc.', 12.254, 422, does_not_raise()),
        ]
    )
    async def test_post_incorrect_submenu(
            self, ac: AsyncClient, title, description, status_code, expectation, get_menu_id) -> None:
        """
        Test POST request for api/v1/menus/{menu_id}/submenus/ if request body is not correct

        :param title: str title submenu
        :param description: str description submenu
        :param status_code: expected status code
        :param expectation: it is expected to be no raise errors. alias for nullcontext
        :param get_menu_id: str menu_id from fixture
        :return: None

        Scenarios:
        - Title is not string
        - Description is not string

        Expected result:
        - The response status code equal 422.
        """
        with expectation:
            response = await ac.post(f'/api/v1/menus/{get_menu_id}/submenus/', json={
                'title': title,
                'description': description
            })
            assert response.status_code == status_code

    async def test_get_submenu_by_id(self, ac: AsyncClient, get_menu_id) -> None:
        """
        Test GET request for /api/v1/menus/{get_menu_id}/submenus/

        :param ac: Async client from conftest.py
        :param get_menu_id: str menu_id from fixture
        :return: None

        Scenarios:
        - Add a new submenu
        - Correct id
        - Correct id but not exists in the database
        - Incorrect id type

        Expected results:
        - Correct id: The response status code equal 200.
        - Correct id but not exists in the database: the response status code equal 404.
            The response body equal {'detail': 'submenu not found'}.
        - Incorrect id type: the response status code equal 404.
            The response body equal {'detail': error message}.
        """
        response = await ac.post(f'/api/v1/menus/{get_menu_id}/submenus/', json={
            'title': 'specific_submenu',
            'description': 'description'
        })
        specific_submenu = response.json()
        response = await ac.get(f'/api/v1/menus/{get_menu_id}/submenus/{specific_submenu.get("id")}')
        assert response.status_code == 200
        assert response.json() == specific_submenu
        response = await ac.get(f'/api/v1/menus/{get_menu_id}/submenus/{self.random_id}')
        assert response.status_code == 404
        assert response.json() == {'detail': 'submenu not found'}
        response = await ac.get(f'/api/v1/menus/{get_menu_id}/submenus/{self.invalid_id}')
        assert response.status_code == 404
        assert response.json() == {
            'detail': f"<class 'asyncpg.exceptions.DataError'>: invalid input for query argument $1:"
                      f" '{self.invalid_id}' (invalid UUID '{self.invalid_id}': length must be between 32..36"
                      f' characters, got 11)'}

    async def test_update_submenu(self, ac: AsyncClient, get_menu_id) -> None:
        """
        Test PATCH request for /api/v1/menus/{menu_id}/submenus/{submenu_id}

        :param ac: Async client from conftest.py
        :param get_menu_id: str menu_id from fixture
        :return: None

        Scenarios:
        - Add new submenu
        - Patch the new submenu
        - Patch a non-existent submenu
        - Send the wrong 'title' type
        - Send the wrong 'description' type

        Expected results:
        - Patch the new submenu: The response status code equal 200. The response 'id' field not changed.
            The response 'title' field has new value. The response 'description' field has new value.
        - Patch a non-existent submenu: The response status code equal 200.
            The response body equal {'detail': 'submenu not found'}
        - Send the wrong 'title' type: The response status code equal 422.
        - Send the wrong 'description' type: The response status code equal 422.
        """
        response = await ac.post(f'/api/v1/menus/{get_menu_id}/submenus/', json={
            'title': 'submenu_for_patch',
            'description': 'description_for_patch'
        })
        submenu_for_update = response.json()
        response = await ac.patch(f'/api/v1/menus/{get_menu_id}/submenus/{submenu_for_update.get("id")}', json={
            'title': 'patched_submenu',
            'description': 'patched_description'
        })
        assert response.status_code == 200
        assert response.json().get('id') == submenu_for_update.get('id')
        assert response.json().get('title') == 'patched_submenu'
        assert response.json().get('description') == 'patched_description'
        response = await ac.patch(f'/api/v1/menus/{get_menu_id}/submenus/{self.random_id}', json={
            'title': 'patched_submenu',
            'description': 'patched_description'
        })
        assert response.status_code == 404
        assert response.json() == {'detail': 'submenu not found'}
        response = await ac.patch(f'/api/v1/menus/{get_menu_id}/submenus/{submenu_for_update.get("id")}', json={
            'title': 25.65,
            'description': 'patched_description'
        })
        assert response.status_code == 422
        response = await ac.patch(f'/api/v1/menus/{get_menu_id}/submenus/{submenu_for_update.get("id")}', json={
            'title': '25.65',
            'description': -5
        })
        assert response.status_code == 422

    async def test_delete_submenu(self, ac: AsyncClient, get_menu_id) -> None:
        """
        Test DELETE request for /api/v1/menus/{menu_id}/submenus/{submenu_id}

        :param ac: Async client from conftest.py
        :param get_menu_id: str menu_id from fixture
        :return: None

        Scenarios:
        - Add new submenu
        - Delete the new submenu
        - Delete the new submenu second time
        - Delete a non-existent submenu
        - Delete a submenu by wrong submenu_id type

        Expected results:
        - Delete the new submenu: The response status code equal 200.
            The response body equal {'status': True, 'message': 'submenu has been deleted'}.
        - Delete the new submenu second time: The response status code equal 200.
            The response body equal {'status': False, 'message': 'submenu not found'}.
        - Delete a non-existent submenu: The response status code equal 200.
            The response body equal {'status': False, 'message': 'submenu not found'}.
        - Delete a menu by wrong submenu_id type: The response status code equal 404.
            The response body equal {'detail': error message}.
        """
        submenu_for_delete = await ac.post(f'/api/v1/menus/{get_menu_id}/submenus/', json={
            'title': 'submenu_for_delete',
            'description': 'submenu_for_delete_description'
        })
        response = await ac.delete(f'/api/v1/menus/{get_menu_id}/submenus/{submenu_for_delete.json().get("id")}')
        assert response.status_code == 200
        assert response.json() == {'status': True, 'message': 'submenu has been deleted'}
        response = await ac.delete(f'/api/v1/menus/{get_menu_id}/submenus/{submenu_for_delete.json().get("id")}')
        assert response.status_code == 200
        assert response.json() == {'status': False, 'message': 'submenu not found'}
        response = await ac.delete(f'/api/v1/menus/{get_menu_id}/submenus/{self.random_id}')
        assert response.status_code == 200
        assert response.json() == {'status': False, 'message': 'submenu not found'}
        response = await ac.delete(f'/api/v1/menus/{get_menu_id}/submenus/{self.invalid_id}')
        assert response.status_code == 404
        assert response.json() == {
            'detail': f"<class 'asyncpg.exceptions.DataError'>: invalid input for query argument $1:"
                      f" '{self.invalid_id}' (invalid UUID '{self.invalid_id}': length must be between 32..36 "
                      f'characters, got 11)'}
