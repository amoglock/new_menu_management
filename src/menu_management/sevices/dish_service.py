from fastapi import BackgroundTasks, Depends, HTTPException

from src.cache.client import RedisClient
from src.database.models import Dish
from src.menu_management.repository.dish_repository import DishRepository
from src.menu_management.schemas.schemas import CreateDish, PatchDish
from src.menu_management.sevices.submenu_service import SubmenuService


class DishService:

    def __init__(self, background_tasks: BackgroundTasks, dish_repository: DishRepository = Depends(),
                 submenu_service: SubmenuService = Depends(), redis_cache: RedisClient = Depends()):
        self.dish_repository = dish_repository
        self.submenu_service = submenu_service
        self.redis_cache = redis_cache
        self.background_task = background_tasks

    async def get_all_dishes(self, submenu_id: str) -> list[Dish]:
        cache = self.redis_cache.get_cache('all_dish', submenu_id)
        if cache:
            return cache
        dishes = await self.dish_repository.get_dish_list(submenu_id)
        self.background_task.add_task(self.redis_cache.set_cache, 'all_dish', submenu_id, dishes)
        return dishes

    async def get_dish(self, dish_id: str) -> Dish:
        cache = self.redis_cache.get_cache('dish', dish_id)
        if cache:
            return cache
        dish = await self.dish_repository.get_dish(dish_id)
        if dish:
            self.background_task.add_task(self.redis_cache.set_cache, 'dish', dish_id, dish)
            return dish
        raise HTTPException(status_code=404, detail='dish not found')

    async def post_dish(self, submenu_id: str, menu_id: str, dish: CreateDish) -> Dish:
        new_dish = dish.to_dict()
        await self.submenu_service.get_submenu(submenu_id)
        new_dish['submenu_group'] = submenu_id
        new_dish['price'] = str('{:.2f}'.format(float(str(new_dish.get('price')))))
        self.background_task.add_task(self.redis_cache.clear_cache, 'all_dish', submenu_id)
        self.background_task.add_task(self.redis_cache.clear_cache, 'submenu', 'all_submenu')
        self.background_task.add_task(self.redis_cache.clear_cache, 'submenu', submenu_id)
        self.background_task.add_task(self.redis_cache.clear_cache, 'menu', 'all_menu')
        self.background_task.add_task(self.redis_cache.clear_cache, 'menu', menu_id)
        self.background_task.add_task(self.redis_cache.set_cache, 'dish', submenu_id, new_dish)
        return await self.dish_repository.add_dish(new_dish)

    async def patch_dish(self, submenu_id: str, dish: PatchDish) -> Dish:
        dish = dish.to_dict()
        try:
            dish['price'] = str('{:.2f}'.format(float(str(dish.get('price')))))
        except ValueError:
            raise HTTPException(status_code=400, detail='price is not digits')
        patched_dish = await self.dish_repository.update_dish(submenu_id, dish)
        if patched_dish:
            self.background_task.add_task(self.redis_cache.clear_cache, 'all_dish', submenu_id)
            self.background_task.add_task(self.redis_cache.set_cache, 'dish', patched_dish.id, patched_dish)
            return patched_dish
        raise HTTPException(status_code=404, detail='dish not found')

    async def delete(self, dish_id: str, submenu_id: str) -> dict[str, bool | str]:
        result = await self.dish_repository.delete_dish(dish_id)
        self.background_task.add_task(self.redis_cache.clear_cache, 'all_dish', submenu_id)
        self.background_task.add_task(self.redis_cache.clear_cache, 'submenu', 'all_submenu')
        self.background_task.add_task(self.redis_cache.clear_cache, 'menu', 'all_menu')
        self.background_task.add_task(self.redis_cache.clear_cache, 'dish', dish_id)
        return result
