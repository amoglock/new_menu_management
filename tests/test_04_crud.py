import pytest
from httpx import AsyncClient


@pytest.mark.usefixtures('clear_db')
class TestScenarioCRUD:
    """
    Class to test scenario. The database must be empty before tests. Uses fixture 'clear_db' for it.

    Scenario:
    - Create a new menu
    - Create a new submenu
    - Create a new dish
    - Create another one a new dish
    - Get specific menu
    - Get specific submenu
    - Delete the submenu
    - Get submenu list
    - Get dish list
    - Get specific menu
    - Delete the menu
    - Get menu list

    -Expected results:
    - Create a new menu: The response status code equal HTTP 201 CREATED.
                        self.menu_id & response_id are equal.
    - Create a new submenu: The response status code equal HTTP 201 CREATED.
                            self.submenu_id & response_id are equal.
    - Create a new dish: The response status code equal HTTP 201 CREATED.
                        self.submenu_id & response_id are equal.
    - Create another one a new dish: The response status code equal HTTP 201 CREATED.
                                    self.submenu_id & response_id are equal.
    - Get specific menu: The response status code equal HTTP 200 OK.
                        self.menu_id & response_id are equal.
                        'submenus_count' from environment & response are equal.
                        'dishes_count' from environment & response are equal.
    - Get specific submenu: The response status code equal HTTP 200 OK.
                        self.menu_id & response_id are equal.
                        'dishes_count' from environment & response are equal.
    - Delete the submenu: The response status code equal HTTP 200 OK.
    - Get submenu list: The response status code equal HTTP 200 OK.
                        The response is empty list
    - Get dish list: The response status code equal HTTP 200 OK.
                        The response is empty list
    - Get specific menu: The response status code equal HTTP 200 OK.
                        self.menu_id & response_id are equal.
                        'submenus_count' from environment & response are equal.
                        'dishes_count' from environment & response are equal.
    - Delete the menu: The response status code equal HTTP 200 OK.
    - Get menu list: The response status code equal HTTP 200 OK.
                    The response is empty list
    """
    menu_id: str
    submenu_id: str
    dish_id: str
    dish_1_id: str
    submenus_count: int = 0
    dishes_count: int = 0

    async def test_scenario(self, ac: AsyncClient):
        # Create a new menu
        response = await ac.post('/api/v1/menus/', json={
            'title': 'test_menu',
            'description': 'test_menu_description'
        })
        self.menu_id = response.json().get('id')
        assert response.status_code == 201
        assert response.json().get('id') == self.menu_id

        # Create a new submenu
        response = await ac.post(f'/api/v1/menus/{self.menu_id}/submenus/', json={
            'title': 'test_submenu',
            'description': 'test_submenu_description'
        })
        self.submenu_id = response.json().get('id')
        assert response.status_code == 201
        assert response.json().get('id') == self.submenu_id
        self.submenus_count += 1

        # Create a new dish
        response = await ac.post(f'/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}/dishes/', json={
            'title': 'test_dish',
            'description': 'test_dish_description',
            'price': '13.50'
        })
        self.dish_id = response.json().get('id')
        assert response.status_code == 201
        assert response.json().get('id') == self.dish_id
        self.dishes_count += 1

        # Create another one a new dish
        response = await ac.post(f'/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}/dishes/', json={
            'title': 'test_dish_1',
            'description': 'test_dish_description_1',
            'price': '12.50'
        })
        self.dish_1_id = response.json().get('id')
        assert response.status_code == 201
        assert response.json().get('id') == self.dish_1_id
        self.dishes_count += 1

        # Get specific menu
        response = await ac.get(f'api/v1/menus/{self.menu_id}')
        assert response.status_code == 200
        assert response.json().get('id') == self.menu_id
        assert response.json().get('submenus_count') == self.submenus_count
        assert response.json().get('dishes_count') == self.dishes_count

        # Get specific submenu
        response = await ac.get(f'/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}')
        assert response.status_code == 200
        assert response.json().get('id') == self.submenu_id
        assert response.json().get('dishes_count') == self.dishes_count

        # Delete submenu
        response = await ac.delete(f'/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}')
        assert response.status_code == 200
        self.submenus_count = 0
        self.dishes_count = 0

        # Get submenu list
        response = await ac.get(f'/api/v1/menus/{self.menu_id}/submenus/')
        assert response.status_code == 200
        assert response.json() == []

        # Get dish list
        response = await ac.get(f'/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}/dishes/')
        assert response.status_code == 200
        assert response.json() == []

        # Get specific menu
        response = await ac.get(f'api/v1/menus/{self.menu_id}')
        assert response.status_code == 200
        assert response.json().get('id') == self.menu_id
        assert response.json().get('submenus_count') == self.submenus_count
        assert response.json().get('dishes_count') == self.dishes_count

        # Delete menu
        response = await ac.delete(f'/api/v1/menus/{self.menu_id}')
        assert response.status_code == 200

        # Get menu list
        response = await ac.get('/api/v1/menus/')
        assert response.status_code == 200
        assert response.json() == []
