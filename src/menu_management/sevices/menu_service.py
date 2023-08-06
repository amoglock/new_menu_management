from fastapi import HTTPException

from ..repository.menu_repository import MenuRepository
from ..schemas import CreateMenu, MenuResponse, PatchMenu
from ..utils import dishes_counter, submenus_counter


class MenuService:

    @classmethod
    def get_all_menu(cls) -> list[MenuResponse] | list:
        menus = MenuRepository.get_all_menu()
        return menus

    @classmethod
    def get_menu(cls, menu_id: str) -> dict:
        menu = MenuRepository.get_menu(menu_id)

        if menu is None:
            raise HTTPException(status_code=404, detail='menu not found')

        submenus_count = submenus_counter(menu.get('id'))
        dish_count = dishes_counter(menu_id=menu.get('id'))
        menu = MenuResponse(**menu, submenus_count=submenus_count, dishes_count=dish_count)
        return menu.model_dump()

    @classmethod
    def post_menu(cls, menu: CreateMenu) -> MenuResponse:
        new_menu = menu.to_dict()
        new_menu = MenuRepository.post_menu(new_menu)
        return new_menu

    @classmethod
    def patch_menu(cls, menu_id: str, menu: PatchMenu):
        menu = menu.to_dict()
        patched_menu = MenuRepository.patch_menu(menu_id, menu)
        if not patched_menu:
            raise HTTPException(status_code=404, detail='menu not found')
        return patched_menu

    @classmethod
    def delete(cls, menu_id: str):
        result = MenuRepository.delete(menu_id)
        return result

    @classmethod
    def count(cls):
        counter = MenuRepository.count()
        return counter

    @classmethod
    def delete_all(cls):
        MenuRepository.delete_all()
