from typing import List

from fastapi import APIRouter

from ..schemas import MenuResponse, CreateMenu, PatchMenu
from ..sevices.menu_service import MenuService

menu_router = APIRouter(
    prefix="/api/v1/menus",
    tags=["menu management"]
)


@menu_router.get("/", response_model=List[MenuResponse], status_code=200)
async def get_all_menus():
    return MenuService.get_all_menu()


@menu_router.get("/{menu_id}", response_model=MenuResponse, status_code=200)
async def get_specific_menu(menu_id: str):
    return MenuService.get_menu(menu_id)


@menu_router.post("/", response_model=MenuResponse, status_code=201)
async def post_new_menu(new_menu: CreateMenu):
    return MenuService.post_menu(new_menu)


@menu_router.patch("/{menu_id}", response_model=MenuResponse, status_code=200)
async def patch_menu(menu_id: str, new_menu: PatchMenu):
    return MenuService.patch_menu(menu_id=menu_id, menu=new_menu)


@menu_router.delete("/{menu_id}", response_model=dict, status_code=200)
async def delete_menu(menu_id: str):
    return MenuService.delete(menu_id)
