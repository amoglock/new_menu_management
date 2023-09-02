import pytest
from httpx import AsyncClient


@pytest.mark.usefixtures('clear_db')
class TestScenarioCRUD:
    menu_id: str

    async def test_scenario(self, ac: AsyncClient):
        response = await ac.post('/api/v1/menus/', json={
            'title': 'test_menu',
            'description': 'test_menu_description'
        })
        self.menu_id = response.json().get('id')
        assert response.status_code == 201
        assert response.json().get('id') == self.menu_id
