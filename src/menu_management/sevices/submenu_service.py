from fastapi import BackgroundTasks, Depends, HTTPException

from src.cache.client import RedisClient
from src.database.models import Submenu

# from cache.client import clear_cache, get_cache, set_cache
from src.menu_management.repository.submenu_repository import SubmenuRepository
from src.menu_management.schemas.schemas import (
    CreateSubmenu,
    PatchSubmenu,
    SubmenuResponse,
)
from src.menu_management.utils import dishes_counter


class SubmenuService:

    def __init__(self, background_tasks: BackgroundTasks, submenu_repository: SubmenuRepository = Depends(),
                 redis_cache: RedisClient = Depends()):
        self.submenu_repository = submenu_repository
        self.redis_cache = redis_cache
        self.background_task = background_tasks

    async def get_all_submenus(self, menu_id: str) -> list[SubmenuResponse]:
        cache = self.redis_cache.get_cache('submenu', 'all_submenu')
        if cache:
            return cache
        submenu_list = await self.submenu_repository.get_list_submenus(menu_id)
        self.background_task.add_task(self.redis_cache.set_cache, 'submenu', 'all_submenu', submenu_list)
        return [await self.__turn_to_model(submenu) for submenu in submenu_list]

    async def get_submenu(self, submenu_id: str) -> SubmenuResponse:
        cache = self.redis_cache.get_cache('submenu', submenu_id)
        if cache:
            return cache
        submenu = await self.submenu_repository.get_submenu(submenu_id)
        self.background_task.add_task(self.redis_cache.set_cache, 'submenu', submenu_id, submenu)
        await self.__check_response(submenu)
        return await self.__turn_to_model(submenu)

    async def post_submenu(self, menu_id: str, submenu: CreateSubmenu) -> Submenu:
        new_submenu = submenu.to_dict()
        new_submenu['menu_group'] = menu_id
        new_submenu = await self.submenu_repository.add_submenu(new_submenu)
        self.background_task.add_task(self.redis_cache.clear_cache, 'submenu', 'all_submenu')
        self.background_task.add_task(self.redis_cache.clear_cache, 'menu', 'all_menu')
        self.background_task.add_task(self.redis_cache.clear_cache, 'menu', menu_id)
        self.background_task.add_task(self.redis_cache.set_cache, 'submenu', new_submenu.id, new_submenu)
        return new_submenu

    async def patch_submenu(self, submenu_id: str, submenu: PatchSubmenu) -> SubmenuResponse:
        submenu = submenu.to_dict()
        patched_submenu = await self.submenu_repository.update_submenu(submenu_id, submenu)
        self.background_task.add_task(self.redis_cache.clear_cache, 'submenu', 'all_submenu')
        self.background_task.add_task(self.redis_cache.set_cache, 'submenu', submenu_id, patched_submenu)
        await self.__check_response(patched_submenu)
        return await self.__turn_to_model(patched_submenu)

    async def delete(self, submenu_id: str, menu_id: str) -> dict[str, str | bool]:
        result = await self.submenu_repository.delete_submenu(submenu_id)
        self.background_task.add_task(self.redis_cache.clear_cache, 'submenu', 'all_submenu')
        self.background_task.add_task(self.redis_cache.clear_cache, 'submenu', submenu_id)
        self.background_task.add_task(self.redis_cache.clear_cache, 'menu', 'all_menu')
        self.background_task.add_task(self.redis_cache.clear_cache, 'menu', menu_id)
        self.background_task.add_task(self.redis_cache.clear_cache, 'dish', submenu_id)
        self.background_task.add_task(self.redis_cache.clear_cache, 'all_dish', submenu_id)
        await self.__check_response(result)
        return result

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
