from typing import List

from fastapi import APIRouter

from ..schemas import DishResponse, CreateDish, PatchDish
from ..sevices.dish_service import DishService

dish_router = APIRouter(
    prefix="/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes",
    tags=["dish management"]
)


@dish_router.get("/", response_model=List[DishResponse], status_code=200)
async def get_all_dishes(submenu_id: str):
    return DishService.get_all_dishes(submenu_id)


@dish_router.get("/{dish_id}", response_model=DishResponse, status_code=200)
async def get_specific_dish(dish_id: str):
    return DishService.get_dish(dish_id)


@dish_router.post("/", response_model=DishResponse, status_code=201)
async def add_dish(submenu_id: str, new_submenu: CreateDish):
    return DishService.post_dish(submenu_id, new_submenu)


@dish_router.patch("/{dish_id}", response_model=DishResponse, status_code=200)
async def patch_menu(dish_id: str, new_submenu: PatchDish):
    return DishService.patch_dish(dish_id, new_submenu)


@dish_router.delete("/{dish_id}", response_model=dict, status_code=200)
async def delete_menu(dish_id: str):
    return DishService.delete(dish_id)
