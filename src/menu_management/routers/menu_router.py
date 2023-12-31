from typing import Union

from fastapi import APIRouter, Depends

from src.menu_management.schemas.schemas import CreateMenu, MenuResponse, PatchMenu
from src.menu_management.sevices.menu_service import MenuService

menu_router = APIRouter(
    prefix='/api/v1/menus',
    tags=['menu management'],
)


@menu_router.get('/', response_model=list[MenuResponse], status_code=200,
                 description='Возвращает список меню которые есть в базе, '
                             'если база пуста - возвращает пустой список', summary='получить список меню')
async def get_all_menus(menu_service: MenuService = Depends()):
    result = await menu_service.get_all_menu()
    return result


@menu_router.get('/getbase', status_code=200)
async def get_base(menu_service: MenuService = Depends()):
    result = await menu_service.get_whole_base()
    return result


@menu_router.get('/{menu_id}', response_model=MenuResponse, status_code=200,
                 description='Возвращает экземпляр определенного меню по переданному menu_id. Если menu_id не найден - '
                             'вызывается исключение с ошибкой 404', summary='получить определенное меню')
async def get_specific_menu(menu_id: str, menu_service: MenuService = Depends()):
    return await menu_service.get_menu(menu_id)


@menu_router.post('/', response_model=MenuResponse, status_code=201,
                  description='Создает новое меню. Принимает схему с названием и описанием. '
                              'Возвращает объект нового меню', summary='создать новое меню')
async def post_new_menu(new_menu: CreateMenu, menu_service: MenuService = Depends()):
    return await menu_service.post_menu(new_menu)


@menu_router.patch('/{menu_id}', response_model=MenuResponse, status_code=200,
                   description='Изменяет существующее меню. Принимает menu_id для поиска и схему с новыми данными.'
                               'Возвращает обновленный экземпляр. Если menu_id не найден - '
                               'вызывается исключение с ошибкой 404', summary='Изменить существующее меню')
async def patch_menu(menu_id: str, new_menu: PatchMenu, menu_service: MenuService = Depends()):
    return await menu_service.patch_menu(menu_id=menu_id, menu=new_menu)


@menu_router.delete('/{menu_id}', response_model=dict[str, Union[str, bool]], status_code=200,
                    description='Удаляет существующее меню. Принимает menu_id для поиска.'
                                'Возвращает словарь с информацией, что удаление совершено.', summary='удалить меню')
async def delete_menu(menu_id: str, menu_service: MenuService = Depends()):
    return await menu_service.delete(menu_id)
