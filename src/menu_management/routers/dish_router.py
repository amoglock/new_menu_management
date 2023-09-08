from typing import Union

from fastapi import APIRouter

from src.menu_management.schemas.schemas import CreateDish, DishResponse, PatchDish
from src.menu_management.sevices.dish_service import DishService

dish_router = APIRouter(
    prefix='/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes',
    tags=['dish management']
)


@dish_router.get('/', response_model=list[DishResponse], status_code=200,
                 description='Возвращает список блюд для подменю, если  submenu_id не существует или блюд нет'
                             ' - возвращает пустой список', summary='получить список блюд')
async def get_all_dishes(submenu_id: str):
    return await DishService.get_all_dishes(submenu_id)


@dish_router.get('/{dish_id}', response_model=DishResponse, status_code=200,
                 description='Возвращает экземпляр определенного блюда по переданному dish_id. '
                             'Если dish_id не найден - вызывается исключение с ошибкой 404',
                 summary='получить определенное блюдо')
async def get_specific_dish(dish_id: str):
    return await DishService.get_dish(dish_id)


@dish_router.post('/', response_model=DishResponse, status_code=201,
                  description='Создает новое блюдо. Принимает схему с названием, описанием и ценой. '
                              'Возвращает объект нового блюда', summary='создать новое блюдо')
async def add_dish(submenu_id: str, menu_id: str, new_submenu: CreateDish):
    return await DishService.post_dish(submenu_id, menu_id, new_submenu)


@dish_router.patch('/{dish_id}', response_model=DishResponse, status_code=200,
                   description='Изменяет существующее блюдо. Принимает dish_id для поиска и схему с новыми данными.'
                               'Возвращает обновленный экземпляр. Если dish_id не найден - '
                               'вызывается исключение с ошибкой 404', summary='Изменить существующее блюдо')
async def patch_menu(dish_id: str, new_submenu: PatchDish):
    return await DishService.patch_dish(dish_id, new_submenu)


@dish_router.delete('/{dish_id}', response_model=dict[str, Union[str, bool]], status_code=200,
                    description='Удаляет существующее блюдо. Принимает dish_id для поиска.'
                                'Возвращает словарь с информацией, что удаление совершено.', summary='удалить меню')
async def delete_menu(dish_id: str, submenu_id: str):
    return await DishService.delete(dish_id, submenu_id)
