from fastapi import HTTPException

# from cache.client import clear_cache, get_cache, set_cache
from src.menu_management.repository.submenu_repository import SubmenuRepository
from src.menu_management.schemas.schemas import (
    CreateSubmenu,
    PatchSubmenu,
    SubmenuResponse,
)
from src.menu_management.utils import dishes_counter


class SubmenuService:

    @classmethod
    async def get_all_submenus(cls, menu_id: str) -> list[SubmenuResponse]:
        # cache = get_cache('submenu', 'all_submenu')
        # if cache:
        #     return cache
        submenu_list = await SubmenuRepository.get_list_submenus(menu_id)

        if submenu_list:
            return [await cls.__turn_to_model(submenu) for submenu in submenu_list]
        raise HTTPException(status_code=404, detail='wrong menu id')
        # set_cache('submenu', 'all_submenu', submenus)

    @classmethod
    async def get_submenu(cls, submenu_id: str) -> SubmenuResponse:
        submenu = await SubmenuRepository.get_submenu(submenu_id)
        await cls.__check_response(submenu)
        return await cls.__turn_to_model(submenu)

        # cache = get_cache('submenu', submenu_id)
        # if cache:
        #     return cache
        # set_cache('submenu', submenu_id, submenu.model_dump())

    @classmethod
    async def post_submenu(cls, menu_id: str, submenu: CreateSubmenu) -> SubmenuResponse:
        new_submenu = submenu.to_dict()
        new_submenu['menu_group'] = menu_id
        new_submenu = await SubmenuRepository.add_submenu(new_submenu)
        if new_submenu:
            # clear_cache('submenu', 'all_submenu')
            # clear_cache('menu', 'all_menu')
            # clear_cache('menu', menu_id)
            # set_cache('submenu', new_submenu.id, new_submenu)
            return new_submenu
        raise HTTPException(status_code=404, detail='wrong menu id')

    @classmethod
    async def patch_submenu(cls, submenu_id: str, submenu: PatchSubmenu) -> SubmenuResponse:
        submenu = submenu.to_dict()
        patched_submenu = await SubmenuRepository.update_submenu(submenu_id, submenu)
        await cls.__check_response(patched_submenu)
        return await cls.__turn_to_model(patched_submenu)
        # clear_cache('submenu', 'all_submenu')
        # set_cache('submenu', submenu_id, patched_submenu)

    @classmethod
    async def delete(cls, submenu_id: str, menu_id: str) -> dict[str, str | bool]:
        result = await SubmenuRepository.delete_submenu(submenu_id)
        await cls.__check_response(result)
        return result
        # clear_cache('submenu', 'all_submenu')
        # clear_cache('submenu', submenu_id)
        # clear_cache('menu', 'all_menu')
        # clear_cache('menu', menu_id)
        # clear_cache('dish', submenu_id)
        # clear_cache('all_dish', submenu_id)

    @classmethod
    async def count(cls) -> int:
        counter = await SubmenuRepository.count()
        return counter

    @staticmethod
    async def __turn_to_model(orm_response) -> SubmenuResponse:
        return SubmenuResponse(id=orm_response.id,
                               title=orm_response.title,
                               description=orm_response.description,
                               dishes_count=await dishes_counter(submenu_id=orm_response.id))

    @staticmethod
    async def __check_response(orm_response) -> None:
        if not orm_response:
            raise HTTPException(status_code=404, detail='submenu not found')
