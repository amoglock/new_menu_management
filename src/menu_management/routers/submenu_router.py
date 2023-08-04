from typing import List

from fastapi import APIRouter

from ..schemas import CreateSubmenu, SubmenuResponse, PatchSubmenu
from ..sevices.submenu_servise import SubmenuService

submenu_router = APIRouter(
    prefix="/api/v1/menus/{menu_id}/submenus",
    tags=["submenu management"]
)


@submenu_router.get("/", response_model=List[SubmenuResponse], status_code=200)
async def get_submenus(menu_id: str):
    return SubmenuService.get_all_submenus(menu_id)


@submenu_router.get("/{submenu_id}", response_model=SubmenuResponse, status_code=200)
async def get_specific_submenu(submenu_id: str):
    return SubmenuService.get_submenu(submenu_id)


@submenu_router.post("/", response_model=SubmenuResponse, status_code=201)
async def add_submenu(menu_id: str, new_submenu: CreateSubmenu):
    return SubmenuService.post_submenu(menu_id, new_submenu)


@submenu_router.patch("/{submenu_id}", response_model=SubmenuResponse, status_code=200)
async def patch_menu(submenu_id: str, new_submenu: PatchSubmenu):
    return SubmenuService.patch_submenu(submenu_id, new_submenu)


@submenu_router.delete("/{submenu_id}", response_model=dict, status_code=200)
async def delete_menu(submenu_id: str):
    return SubmenuService.delete(submenu_id)
