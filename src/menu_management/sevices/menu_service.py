from fastapi import HTTPException

from cache.client import clear_cache, get_cache, redis_client, set_cache

from ..repository.menu_repository import MenuRepository
from ..schemas import CreateMenu, MenuResponse, PatchMenu
from ..utils import dishes_counter, submenus_counter


class MenuService:

    @classmethod
    def get_all_menu(cls) -> list[MenuResponse] | list:
        cache = get_cache('menu', 'all_menu')
        if cache:
            return cache
        menus = MenuRepository.get_all_menu()
        set_cache('menu', 'all_menu', menus)
        return menus

    @classmethod
    def get_menu(cls, menu_id: str) -> dict:
        menu = MenuRepository.get_menu(menu_id)

        if menu is None:
            raise HTTPException(status_code=404, detail='menu not found')

        cache = get_cache('menu', menu_id)
        if cache:
            return cache

        submenus_count = submenus_counter(menu.get('id'))
        dish_count = dishes_counter(menu_id=menu.get('id'))
        menu = MenuResponse(**menu, submenus_count=submenus_count, dishes_count=dish_count)
        set_cache('menu', menu_id, menu)
        return menu.model_dump()

    @classmethod
    def post_menu(cls, menu: CreateMenu) -> MenuResponse:
        new_menu = menu.to_dict()
        new_menu = MenuRepository.post_menu(new_menu)
        set_cache('menu', new_menu.id, new_menu)
        clear_cache('menu', 'all_menu')
        return new_menu

    @classmethod
    def patch_menu(cls, menu_id: str, menu: PatchMenu) -> MenuResponse | dict:
        menu = menu.to_dict()
        patched_menu = MenuRepository.patch_menu(menu_id, menu)
        if not patched_menu:
            raise HTTPException(status_code=404, detail='menu not found')
        clear_cache('menu', 'all_menu')
        set_cache('menu', menu_id, patched_menu)
        return patched_menu

    @classmethod
    def delete(cls, menu_id: str) -> dict:
        result = MenuRepository.delete(menu_id)
        clear_cache('menu', 'all_menu')
        clear_cache('menu', menu_id)
        return result

    @classmethod
    def count(cls) -> int:
        counter = MenuRepository.count()
        return counter

    @classmethod
    def delete_all(cls) -> None:
        redis_client.flushdb()
        MenuRepository.delete_all()
