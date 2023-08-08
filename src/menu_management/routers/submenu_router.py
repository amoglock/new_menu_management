from fastapi import APIRouter

from ..schemas import CreateSubmenu, PatchSubmenu, SubmenuResponse
from ..sevices.submenu_servise import SubmenuService

submenu_router = APIRouter(
    prefix='/api/v1/menus/{menu_id}/submenus',
    tags=['submenu management']
)


@submenu_router.get('/', response_model=list[SubmenuResponse], status_code=200,
                    description='Возвращает список подменю для определенного меню которое есть в базе, '
                                'если подменю нет - возвращает пустой список', summary='получить список подменю')
async def get_submenus(menu_id: str):
    return SubmenuService.get_all_submenus(menu_id)


@submenu_router.get('/{submenu_id}', response_model=SubmenuResponse, status_code=200,
                    description='Возвращает экземпляр определенного подменю по переданному submenu_id. '
                                'Если submenu_id не найден - вызывается исключение с ошибкой 404',
                    summary='получить определенное подменю'
                    )
async def get_specific_submenu(submenu_id: str):
    return SubmenuService.get_submenu(submenu_id)


@submenu_router.post('/', response_model=SubmenuResponse, status_code=201,
                     description='Создает новое подменю. Принимает схему с названием и описанием и menu_id для привязки'
                                 'к существующему меню. Возвращает объект нового меню', summary='создать новое подменю')
async def add_submenu(menu_id: str, new_submenu: CreateSubmenu):
    return SubmenuService.post_submenu(menu_id, new_submenu)


@submenu_router.patch('/{submenu_id}', response_model=SubmenuResponse, status_code=200,
                      description='Изменяет существующее подменю. Принимает submenu_id для поиска и схему с новыми '
                                  'данными. Возвращает обновленный экземпляр. Если submenu_id не найден - '
                                  'вызывается исключение с ошибкой 404', summary='Изменить существующее подменю')
async def patch_menu(submenu_id: str, new_submenu: PatchSubmenu):
    return SubmenuService.patch_submenu(submenu_id, new_submenu)


@submenu_router.delete('/{submenu_id}', response_model=dict, status_code=200,
                       description='Удаляет существующее подменю. Принимает submenu_id для поиска.Возвращает '
                                   'словарь с информацией, что удаление совершено.', summary='удалить подменю')
async def delete_menu(submenu_id: str):
    return SubmenuService.delete(submenu_id)
