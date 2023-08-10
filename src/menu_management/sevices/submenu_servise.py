from fastapi import HTTPException

from cache.client import clear_cache, get_cache, set_cache

from ..repository.submenu_repository import SubmenuRepository
from ..schemas import CreateSubmenu, PatchSubmenu, SubmenuResponse
from ..utils import dishes_counter


class SubmenuService:

    @classmethod
    async def get_all_submenus(cls, menu_id: str) -> list[SubmenuResponse]:
        cache = get_cache('submenu', 'all_submenu')
        if cache:
            return cache
        submenus = SubmenuRepository.get_all_submenus(menu_id)
        set_cache('submenu', 'all_submenu', submenus)
        return submenus

    @classmethod
    async def get_submenu(cls, submenu_id: str) -> dict:
        submenu = SubmenuRepository.get_submenu(submenu_id)

        if not submenu:
            raise HTTPException(status_code=404, detail='submenu not found')

        cache = get_cache('submenu', submenu_id)
        if cache:
            return cache

        dishes_count = dishes_counter(submenu_id=submenu.get('id'))
        submenu = SubmenuResponse(**submenu, dishes_count=dishes_count)
        set_cache('submenu', submenu_id, submenu.model_dump())
        return submenu.model_dump()

    @classmethod
    async def post_submenu(cls, menu_id: str, submenu: CreateSubmenu) -> SubmenuResponse:
        new_submenu = submenu.to_dict()
        new_submenu = SubmenuRepository.post_submenu(menu_id, new_submenu)
        clear_cache('submenu', 'all_submenu')
        clear_cache('menu', 'all_menu')
        clear_cache('menu', menu_id)
        set_cache('submenu', new_submenu.id, new_submenu)
        return new_submenu

    @classmethod
    async def patch_submenu(cls, submenu_id: str, submenu: PatchSubmenu) -> SubmenuResponse | dict:
        submenu = submenu.to_dict()
        patched_submenu = SubmenuRepository.patch_submenu(submenu_id, submenu)
        if not patched_submenu:
            raise HTTPException(status_code=404, detail='submenu not found')
        clear_cache('submenu', 'all_submenu')
        set_cache('submenu', submenu_id, patched_submenu)
        return patched_submenu

    @classmethod
    async def delete(cls, submenu_id: str, menu_id: str) -> dict:
        result = SubmenuRepository.delete(submenu_id)
        clear_cache('submenu', 'all_submenu')
        clear_cache('submenu', submenu_id)
        clear_cache('menu', 'all_menu')
        clear_cache('menu', menu_id)
        clear_cache('dish', submenu_id)
        clear_cache('all_dish', submenu_id)
        return result

    @classmethod
    async def count(cls) -> int:
        counter = SubmenuRepository.count()
        return counter
