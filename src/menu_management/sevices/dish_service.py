from fastapi import HTTPException

from cache.client import clear_cache, get_cache, set_cache

from ..repository.dish_repository import DishRepository
from ..schemas import CreateDish, DishResponse, PatchDish


class DishService:

    @classmethod
    async def get_all_dishes(cls, submenu_id: str) -> list[DishResponse]:
        cache = get_cache('all_dish', submenu_id)
        if cache:
            return cache
        dishes = DishRepository.get_all_dishes(submenu_id)
        set_cache('all_dish', submenu_id, dishes)
        return dishes

    @classmethod
    async def get_dish(cls, dish_id: str) -> dict:
        dish = DishRepository.get_dish(dish_id)
        if not dish:
            raise HTTPException(status_code=404, detail='dish not found')

        cache = get_cache('dish', dish_id)
        if cache:
            return cache
        dish = DishResponse(**dish)
        set_cache('dish', dish_id, dish.model_dump())
        return dish.model_dump()

    @classmethod
    async def post_dish(cls, submenu_id: str, menu_id: str, dish: CreateDish) -> DishResponse:
        new_dish = dish.to_dict()
        new_dish = DishRepository.post_dish(submenu_id, new_dish)
        clear_cache('all_dish', submenu_id)
        clear_cache('submenu', 'all_submenu')
        clear_cache('submenu', submenu_id)
        clear_cache('menu', 'all_menu')
        clear_cache('menu', menu_id)
        set_cache('dish', submenu_id, new_dish)
        return new_dish

    @classmethod
    async def patch_dish(cls, submenu_id: str, submenu: PatchDish) -> DishResponse | dict:
        submenu = submenu.to_dict()
        patched_dish = DishRepository.patch_dish(submenu_id, submenu)
        if not patched_dish:
            raise HTTPException(status_code=404, detail='submenu not found')
        clear_cache('all_dish', submenu_id)
        set_cache('dish', patched_dish['id'], patched_dish)
        return patched_dish

    @classmethod
    async def delete(cls, dish_id: str, submenu_id: str) -> dict:
        result = DishRepository.delete(dish_id)
        clear_cache('all_dish', submenu_id)
        clear_cache('submenu', 'all_submenu')
        clear_cache('menu', 'all_menu')
        clear_cache('dish', dish_id)
        return result

    @classmethod
    async def count(cls) -> int:
        counter = DishRepository.count()
        return counter
