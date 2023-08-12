from fastapi import HTTPException

# from cache.client import clear_cache, get_cache, redis_client, set_cache
from menu_management.repository.menu_repository import MenuRepository
from menu_management.schemas import CreateMenu, MenuResponse, PatchMenu
from menu_management.utils import dishes_counter, submenus_counter


class MenuService:

    @classmethod
    async def get_all_menu(cls) -> list[MenuResponse] | None:
        # cache = get_cache('menu', 'all_menu')
        # if isinstance(cache, list):
        #     return cache
        menus = await MenuRepository.get_menu_list()
        # await set_cache('menu', 'all_menu', menus)
        return [await cls.__turn_to_model(menu) for menu in menus]

    #
    @classmethod
    async def get_menu(cls, menu_id: str) -> MenuResponse:
        menu = await MenuRepository.get_menu(menu_id)
        await cls.__check_response(menu)
        return await cls.__turn_to_model(menu)

        # cache = get_cache('menu', menu_id)
        # if cache:
        #     return cache
        # set_cache('menu', menu_id, menu)

    @classmethod
    async def post_menu(cls, new_menu: CreateMenu) -> MenuResponse:
        new_menu = new_menu.to_dict()
        added_menu = await MenuRepository.add_new_menu(new_menu)
        # set_cache('menu', new_menu.id, new_menu)
        # clear_cache('menu', 'all_menu')
        return added_menu

    @classmethod
    async def patch_menu(cls, menu_id: str, menu: PatchMenu) -> MenuResponse:
        menu = menu.to_dict()
        patched_menu = await MenuRepository.patch_menu(menu_id, menu)
        await cls.__check_response(patched_menu)
        return await cls.__turn_to_model(patched_menu)
        # clear_cache('menu', 'all_menu')
        # set_cache('menu', menu_id, patched_menu)

    @classmethod
    async def delete(cls, menu_id: str) -> dict[str, str | bool]:
        result = await MenuRepository.delete(menu_id)
        # print(result)
        # await cls.__check_response(result)
        # clear_cache('menu', 'all_menu')
        # clear_cache('menu', menu_id)
        return result

    @classmethod
    async def count_menu(cls) -> int:
        counter = await MenuRepository.count()
        return counter

    @classmethod
    async def delete_all(cls) -> None:
        # redis_client.flushdb()
        MenuRepository.delete_all()

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
