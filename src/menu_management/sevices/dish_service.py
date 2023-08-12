from fastapi import HTTPException

# from cache.client import clear_cache, get_cache, set_cache
from menu_management.repository.dish_repository import DishRepository
from menu_management.schemas import CreateDish, DishResponse, PatchDish
from menu_management.sevices.submenu_servise import SubmenuService


class DishService:

    @classmethod
    async def get_all_dishes(cls, submenu_id: str) -> list[DishResponse]:
        # cache = get_cache('all_dish', submenu_id)
        # if cache:
        #     return cache
        dishes = await DishRepository.get_dish_list(submenu_id)
        # set_cache('all_dish', submenu_id, dishes)
        return dishes

    @classmethod
    async def get_dish(cls, dish_id: str) -> DishResponse:
        dish = await DishRepository.get_dish(dish_id)
        if dish:
            return dish
        raise HTTPException(status_code=404, detail='dish not found')

        # cache = get_cache('dish', dish_id)
        # if cache:
        #     return cache
        # set_cache('dish', dish_id, dish.model_dump())

    @classmethod
    async def post_dish(cls, submenu_id: str, menu_id: str, dish: CreateDish) -> DishResponse:
        new_dish = dish.to_dict()
        await SubmenuService.get_submenu(submenu_id)
        new_dish['submenu_group'] = submenu_id
        new_dish['price'] = str('{:.2f}'.format(float(str(new_dish.get('price')))))
        return await DishRepository.add_dish(new_dish)
        # clear_cache('all_dish', submenu_id)
        # clear_cache('submenu', 'all_submenu')
        # clear_cache('submenu', submenu_id)
        # clear_cache('menu', 'all_menu')
        # clear_cache('menu', menu_id)
        # set_cache('dish', submenu_id, new_dish)

    @classmethod
    async def patch_dish(cls, submenu_id: str, dish: PatchDish) -> DishResponse:
        dish = dish.to_dict()
        try:
            dish['price'] = str('{:.2f}'.format(float(str(dish.get('price')))))
        except ValueError:
            raise HTTPException(status_code=400, detail='price is not digits')
        patched_dish = await DishRepository.update_dish(submenu_id, dish)
        if patched_dish:
            return patched_dish
        raise HTTPException(status_code=404, detail='dish not found')
        # clear_cache('all_dish', submenu_id)
        # set_cache('dish', patched_dish['id'], patched_dish)

    @classmethod
    async def delete(cls, dish_id: str, submenu_id: str) -> dict[str, bool | str]:
        result = await DishRepository.delete_dish(dish_id)
        # clear_cache('all_dish', submenu_id)
        # clear_cache('submenu', 'all_submenu')
        # clear_cache('menu', 'all_menu')
        # clear_cache('dish', dish_id)
        return result

    @classmethod
    async def count(cls) -> int:
        counter = await DishRepository.count()
        return counter
