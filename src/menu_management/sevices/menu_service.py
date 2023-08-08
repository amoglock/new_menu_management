import pickle

from fastapi import HTTPException

from cache.client import redis_client

from ..repository.menu_repository import MenuRepository
from ..schemas import CreateMenu, MenuResponse, PatchMenu
from ..utils import dishes_counter, submenus_counter


class MenuService:

    @classmethod
    def get_all_menu(cls) -> list[MenuResponse] | list:
        cache = redis_client.get('all_menu')
        if cache is not None:
            return pickle.loads(cache)
        menus = MenuRepository.get_all_menu()
        redis_client.set('all_menu', pickle.dumps(menus))
        return menus

    @classmethod
    def get_menu(cls, menu_id: str) -> dict:
        menu = MenuRepository.get_menu(menu_id)

        if menu is None:
            raise HTTPException(status_code=404, detail='menu not found')

        cache = redis_client.get('specific_menu')
        if cache is not None and pickle.loads(cache).id == menu_id:
            return pickle.loads(cache)

        submenus_count = submenus_counter(menu.get('id'))
        dish_count = dishes_counter(menu_id=menu.get('id'))
        menu = MenuResponse(**menu, submenus_count=submenus_count, dishes_count=dish_count)
        redis_client.set('specific_menu', pickle.dumps(menu))
        return menu.model_dump()

    @classmethod
    def post_menu(cls, menu: CreateMenu) -> MenuResponse:
        new_menu = menu.to_dict()
        new_menu = MenuRepository.post_menu(new_menu)
        redis_client.delete('all_menu')
        return new_menu

    @classmethod
    def patch_menu(cls, menu_id: str, menu: PatchMenu):
        menu = menu.to_dict()
        patched_menu = MenuRepository.patch_menu(menu_id, menu)
        if not patched_menu:
            raise HTTPException(status_code=404, detail='menu not found')
        redis_client.delete('all_menu', 'specific_menu')
        return patched_menu

    @classmethod
    def delete(cls, menu_id: str):
        result = MenuRepository.delete(menu_id)
        redis_client.delete('all_menu')
        redis_client.delete('specific_menu')
        return result

    @classmethod
    def count(cls) -> int:
        counter = MenuRepository.count()
        return counter

    @classmethod
    def delete_all(cls):
        redis_client.delete('all_menu', 'specific_menu')
        MenuRepository.delete_all()
