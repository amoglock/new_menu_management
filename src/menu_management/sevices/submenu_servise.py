from typing import List

from fastapi import HTTPException

from ..repository.submenu_repository import SubmenuRepository
from ..schemas import SubmenuResponse, CreateSubmenu, PatchSubmenu
from ..utils import dishes_counter


class SubmenuService:

    @classmethod
    def get_all_submenus(cls, menu_id: str) -> List[SubmenuResponse]:
        submenus = SubmenuRepository.get_all_submenus(menu_id)
        return submenus

    @classmethod
    def get_submenu(cls, submenu_id: str) -> dict:
        submenu = SubmenuRepository.get_submenu(submenu_id)
        if not submenu:
            raise HTTPException(status_code=404, detail="submenu not found")
        dishes_count = dishes_counter(submenu_id=submenu.get("id"))
        submenu = SubmenuResponse(**submenu, dishes_count=dishes_count)
        return submenu.model_dump()

    @classmethod
    def post_submenu(cls, menu_id: str, submenu: CreateSubmenu) -> SubmenuResponse:
        new_submenu = submenu.to_dict()
        new_submenu = SubmenuRepository.post_submenu(menu_id, new_submenu)
        return new_submenu

    @classmethod
    def patch_submenu(cls, submenu_id: str, submenu: PatchSubmenu):
        submenu = submenu.to_dict()
        patched_submenu = SubmenuRepository.patch_submenu(submenu_id, submenu)
        if not patched_submenu:
            raise HTTPException(status_code=404, detail="submenu not found")
        return patched_submenu

    @classmethod
    def delete(cls, take_id: str):
        result = SubmenuRepository.delete(take_id)
        return result

    @classmethod
    def count(cls):
        counter = SubmenuRepository.count()
        return counter
