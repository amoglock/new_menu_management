import pickle

from fastapi import HTTPException

from cache.client import redis_client

from ..repository.dish_repository import DishRepository
from ..schemas import CreateDish, DishResponse, PatchDish


class DishService:

    @classmethod
    def get_all_dishes(cls, submenu_id: str) -> list[DishResponse]:
        cache = redis_client.get('all_dishes')
        if cache is not None and pickle.loads(cache)[0].id == submenu_id:
            return pickle.loads(cache)
        dishes = DishRepository.get_all_dishes(submenu_id)
        return dishes

    @classmethod
    def get_dish(cls, dish_id: str) -> dict:
        dish = DishRepository.get_dish(dish_id)
        if not dish:
            raise HTTPException(status_code=404, detail='dish not found')

        cache = redis_client.get('specific_dish')
        if cache is not None and pickle.loads(cache).id == dish_id:
            return pickle.loads(cache)
        dish = DishResponse(**dish)
        redis_client.set('specific_dish', pickle.dumps(dish.model_dump()))
        return dish.model_dump()

    @classmethod
    def post_dish(cls, submenu_id: str, dish: CreateDish) -> DishResponse:
        new_dish = dish.to_dict()
        new_dish = DishRepository.post_dish(submenu_id, new_dish)
        redis_client.delete('all_dishes')
        redis_client.delete('specific_dish')
        return new_dish

    @classmethod
    def patch_dish(cls, submenu_id: str, submenu: PatchDish):
        submenu = submenu.to_dict()
        patched_submenu = DishRepository.patch_dish(submenu_id, submenu)
        if not patched_submenu:
            raise HTTPException(status_code=404, detail='submenu not found')
        redis_client.delete('all_dishes')
        redis_client.delete('specific_dish')
        return patched_submenu

    @classmethod
    def delete(cls, take_id: str):
        result = DishRepository.delete(take_id)
        redis_client.delete('all_dishes')
        redis_client.delete('specific_dish')
        return result

    @classmethod
    def count(cls) -> int:
        counter = DishRepository.count()
        return counter
