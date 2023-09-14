from fastapi import BackgroundTasks, Depends, HTTPException

from src.cache.client import RedisClient, redis_client
from src.database.models import Menu
from src.menu_management.repository.menu_repository import MenuRepository
from src.menu_management.schemas.schemas import CreateMenu, MenuResponse, PatchMenu
from src.menu_management.utils import dishes_counter, submenus_counter


class MenuService:

    def __init__(self, background_tasks: BackgroundTasks, menu_repository: MenuRepository = Depends(),
                 redis_cache: RedisClient = Depends()) -> None:
        self.menu_repository = menu_repository
        self.redis_cache = redis_cache
        self.background_task = background_tasks

    async def get_all_menu(self) -> list[MenuResponse] | None:
        cache = self.redis_cache.get_cache('menu', 'all_menu')
        if cache:
            return cache
        menus = await self.menu_repository.get_menu_list()
        self.background_task.add_task(self.redis_cache.set_cache, 'menu', 'all_menu', menus)
        return [await self.__turn_to_model(menu) for menu in menus]

    async def get_menu(self, menu_id: str) -> MenuResponse:
        cache = self.redis_cache.get_cache('menu', menu_id)
        if cache:
            return cache
        menu = await self.menu_repository.get_menu(menu_id)
        await self.__check_response(menu)
        self.background_task.add_task(self.redis_cache.set_cache, 'menu', menu_id, menu)
        return await self.__turn_to_model(menu)

    async def post_menu(self, new_menu: CreateMenu) -> Menu:
        new_menu = new_menu.to_dict()
        added_menu = await self.menu_repository.add_new_menu(new_menu)
        self.background_task.add_task(self.redis_cache.set_cache, 'menu', added_menu.id, added_menu)
        self.background_task.add_task(self.redis_cache.clear_cache, 'menu', 'all_menu')
        return added_menu

    async def patch_menu(self, menu_id: str, menu: PatchMenu) -> MenuResponse:
        menu = menu.to_dict()
        patched_menu = await self.menu_repository.patch_menu(menu_id, menu)
        await self.__check_response(patched_menu)
        self.background_task.add_task(self.redis_cache.clear_cache, 'menu', 'all_menu')
        self.background_task.add_task(self.redis_cache.set_cache, 'menu', menu_id, patched_menu)
        return await self.__turn_to_model(patched_menu)

    async def delete(self, menu_id: str) -> dict[str, str | bool]:
        result = await self.menu_repository.delete(menu_id)
        await self.__check_response(result)
        self.background_task.add_task(self.redis_cache.clear_cache, 'menu', 'all_menu')
        self.background_task.add_task(self.redis_cache.clear_cache, 'menu', menu_id)
        return result

    async def delete_all(self) -> None:
        self.background_task.add_task(redis_client.flushdb)
        await self.menu_repository.delete_all()

    @staticmethod
    async def __turn_to_model(orm_response) -> MenuResponse:
        return MenuResponse(id=orm_response.id,
                            title=orm_response.title,
                            description=orm_response.description,
                            submenus_count=await submenus_counter(orm_response.id),
                            dishes_count=await dishes_counter(menu_id=orm_response.id))

    @staticmethod
    async def __check_response(orm_response) -> None:
        if not orm_response:
            raise HTTPException(status_code=404, detail='menu not found')
