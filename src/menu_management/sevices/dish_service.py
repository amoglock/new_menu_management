from typing import List

from fastapi import HTTPException

from ..repository.dish_repository import DishRepository
from ..schemas import CreateDish, DishResponse, PatchDish


class DishService:

    @classmethod
    def get_all_dishes(cls, submenu_id: str) -> List[DishResponse]:
        submenus = DishRepository.get_all_dishes(submenu_id)
        return submenus

    @classmethod
    def get_dish(cls, dish_id: str) -> dict:
        dish = DishRepository.get_dish(dish_id)
        if not dish:
            raise HTTPException(status_code=404, detail="dish not found")
        dish = DishResponse(**dish)
        return dish.model_dump()

    @classmethod
    def post_dish(cls, submenu_id: str, dish: CreateDish) -> DishResponse:
        new_dish = dish.to_dict()
        new_dish = DishRepository.post_dish(submenu_id, new_dish)
        return new_dish

    @classmethod
    def patch_dish(cls, submenu_id: str, submenu: PatchDish):
        submenu = submenu.to_dict()
        patched_submenu = DishRepository.patch_dish(submenu_id, submenu)
        if not patched_submenu:
            raise HTTPException(status_code=404, detail="submenu not found")
        return patched_submenu

    @classmethod
    def delete(cls, take_id: str):
        result = DishRepository.delete(take_id)
        return result

    @classmethod
    def count(cls):
        counter = DishRepository.count()
        return counter
