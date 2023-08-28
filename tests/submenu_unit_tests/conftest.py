# import pytest
# from httpx import AsyncClient

# @pytest.fixture
# async def get_menu_id(ac: AsyncClient) -> str:
#     response = await ac.get('/api/v1/menus/')
#     menu_id = response.json()[0].get('id')
#     return menu_id
