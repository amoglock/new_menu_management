import pickle

from fastapi import HTTPException

from cache.client import redis_client

from ..repository.submenu_repository import SubmenuRepository
from ..schemas import CreateSubmenu, PatchSubmenu, SubmenuResponse
from ..utils import dishes_counter


class SubmenuService:

    @classmethod
    def get_all_submenus(cls, menu_id: str) -> list[SubmenuResponse]:
        cache = redis_client.get('all_submenu')
        if cache is not None and pickle.loads(cache)[0].id == menu_id:
            return pickle.loads(cache)
        submenus = SubmenuRepository.get_all_submenus(menu_id)
        redis_client.set('all_submenu', pickle.dumps(submenus))
        return submenus

    @classmethod
    def get_submenu(cls, submenu_id: str) -> dict:
        submenu = SubmenuRepository.get_submenu(submenu_id)

        if not submenu:
            raise HTTPException(status_code=404, detail='submenu not found')

        cache = redis_client.get('specific_submenu')
        if cache is not None and pickle.loads(cache)['id'] == submenu_id:
            return pickle.loads(cache)

        dishes_count = dishes_counter(submenu_id=submenu.get('id'))
        submenu = SubmenuResponse(**submenu, dishes_count=dishes_count)
        redis_client.set('specific_submenu', pickle.dumps(submenu.model_dump()))
        return submenu.model_dump()

    @classmethod
    def post_submenu(cls, menu_id: str, submenu: CreateSubmenu) -> SubmenuResponse:
        new_submenu = submenu.to_dict()
        new_submenu = SubmenuRepository.post_submenu(menu_id, new_submenu)
        redis_client.delete('all_submenu')
        redis_client.delete('specific_submenu')
        return new_submenu

    @classmethod
    def patch_submenu(cls, submenu_id: str, submenu: PatchSubmenu) -> SubmenuResponse | dict:
        submenu = submenu.to_dict()
        patched_submenu = SubmenuRepository.patch_submenu(submenu_id, submenu)
        if not patched_submenu:
            raise HTTPException(status_code=404, detail='submenu not found')
        redis_client.delete('all_submenu')
        redis_client.delete('specific_submenu')
        return patched_submenu

    @classmethod
    def delete(cls, take_id: str) -> dict:
        result = SubmenuRepository.delete(take_id)
        redis_client.delete('all_submenu')
        redis_client.delete('specific_submenu')
        return result

    @classmethod
    def count(cls) -> int:
        counter = SubmenuRepository.count()
        return counter
