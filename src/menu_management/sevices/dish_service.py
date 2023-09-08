from fastapi import Depends, HTTPException

from src.database.models import Dish

# from cache.client import clear_cache, get_cache, set_cache
from src.menu_management.repository.dish_repository import DishRepository
from src.menu_management.schemas.schemas import CreateDish, PatchDish
from src.menu_management.sevices.submenu_servise import SubmenuService


class DishService:

    def __init__(self, dish_repository: DishRepository = Depends(), submenu_service: SubmenuService = Depends()):
        self.dish_repository = dish_repository
        self.submenu_service = submenu_service

    async def get_all_dishes(self, submenu_id: str) -> list[Dish]:
        # cache = get_cache('all_dish', submenu_id)
        # if cache:
        #     return cache
        dishes = await self.dish_repository.get_dish_list(submenu_id)
        # set_cache('all_dish', submenu_id, dishes)
        return dishes

    async def get_dish(self, dish_id: str) -> Dish:
        dish = await self.dish_repository.get_dish(dish_id)
        if dish:
            return dish
        raise HTTPException(status_code=404, detail='dish not found')

        # cache = get_cache('dish', dish_id)
        # if cache:
        #     return cache
        # set_cache('dish', dish_id, dish.model_dump())

    async def post_dish(self, submenu_id: str, menu_id: str, dish: CreateDish) -> Dish:
        new_dish = dish.to_dict()
        await self.submenu_service.get_submenu(submenu_id)
        new_dish['submenu_group'] = submenu_id
        new_dish['price'] = str('{:.2f}'.format(float(str(new_dish.get('price')))))
        return await self.dish_repository.add_dish(new_dish)
        # clear_cache('all_dish', submenu_id)
        # clear_cache('submenu', 'all_submenu')
        # clear_cache('submenu', submenu_id)
        # clear_cache('menu', 'all_menu')
        # clear_cache('menu', menu_id)
        # set_cache('dish', submenu_id, new_dish)

    async def patch_dish(self, submenu_id: str, dish: PatchDish) -> Dish:
        dish = dish.to_dict()
        try:
            dish['price'] = str('{:.2f}'.format(float(str(dish.get('price')))))
        except ValueError:
            raise HTTPException(status_code=400, detail='price is not digits')
        patched_dish = await self.dish_repository.update_dish(submenu_id, dish)
        if patched_dish:
            return patched_dish
        raise HTTPException(status_code=404, detail='dish not found')
        # clear_cache('all_dish', submenu_id)
        # set_cache('dish', patched_dish['id'], patched_dish)

    async def delete(self, dish_id: str, submenu_id: str) -> dict[str, bool | str]:
        result = await self.dish_repository.delete_dish(dish_id)
        # clear_cache('all_dish', submenu_id)
        # clear_cache('submenu', 'all_submenu')
        # clear_cache('menu', 'all_menu')
        # clear_cache('dish', dish_id)
        return result
