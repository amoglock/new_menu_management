from contextlib import nullcontext as does_not_raise

import pytest
from httpx import AsyncClient

from src.menu_management.sevices.menu_service import MenuService


async def test_get_menu_list(ac: AsyncClient):
    response = await ac.get('/api/v1/menus/')
    assert response.json() == []
    assert response.status_code == 200
    await ac.post('/api/v1/menus/', json={
        'title': 'test_menu',
        'description': 'description'
    })
    response = await ac.get('/api/v1/menus/')
    assert len(response.json()) == await MenuService.count_menu()
    assert response.json() == [{'id': response.json()[0].get('id'), 'title': 'test_menu', 'description': 'description',
                                'submenus_count': 0, 'dishes_count': 0}]


@pytest.mark.parametrize(
    'title, description, expectation',
    [
        ('my_menu', 'my_menu_description', does_not_raise()),
        ('my_menu2', 'my_menu_description2', does_not_raise()),
    ]
)
async def test_post_correct_menu(ac: AsyncClient, title, description, expectation):
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
async def test_post_incorrect_menu(ac: AsyncClient, title, description, status_code, expectation):
    with expectation:
        response = await ac.post('/api/v1/menus/', json={
            'title': title,
            'description': description
        })
        assert response.status_code == status_code


async def test_menu_already_exists(ac: AsyncClient):
    response = await ac.post('/api/v1/menus/', json={
        'title': 'my_menu',
        'description': 'my_menu_description'
    })
    assert response.status_code == 409
    assert response.json() == {'detail': 'This menu title already exists'}


async def test_get_specific_menu(ac: AsyncClient):
    random_id = '5f4a67c2-832e-4975-b5cf-c3ed35015d98'
    invalid_id = '5f4a67c2-83'
    response = await ac.post('/api/v1/menus/', json={
        'title': 'specific_menu',
        'description': 'specific_menu_description'
    })
    specific_menu = response.json()
    response = await ac.get(f"api/v1/menus/{specific_menu.get('id')}")
    assert response.status_code == 200
    assert response.json() == specific_menu
    response = await ac.get(f'api/v1/menus/{random_id}')
    assert response.status_code == 404
    assert response.json() == {'detail': 'menu not found'}
    response = await ac.get(f'api/v1/menus/{invalid_id}')
    assert response.status_code == 404
    assert response.json() == {'detail': f"<class 'asyncpg.exceptions.DataError'>: invalid input for query argument $1:"
                                         f" '{invalid_id}' (invalid UUID '{invalid_id}': length must be between 32..36"
                                         f' characters, got 11)'}


async def test_patch_menu(ac: AsyncClient):
    random_id = '5f4a67c2-832e-4975-b5cf-c3ed35015d98'
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
    response = await ac.patch(f'api/v1/menus/{random_id}', json={
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


async def test_delete_menu(ac: AsyncClient):
    random_id = '5f4a67c2-832e-4975-b5cf-c3ed35015d98'
    invalid_id = '5f4a67c2-832e-4975-b5cf-'
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
    response = await ac.delete(f'api/v1/menus/{random_id}')
    assert response.status_code == 200
    assert response.json() == {'status': False, 'message': 'menu not found'}
    response = await ac.delete(f'api/v1/menus/{invalid_id}')
    assert response.status_code == 404
    assert response.json() == {'detail': f"<class 'asyncpg.exceptions.DataError'>: invalid input for query argument $1:"
                                         f" '{invalid_id}' (invalid UUID '{invalid_id}': length must be between 32..36 "
                                         f'characters, got 24)'}
