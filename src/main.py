from fastapi import FastAPI

from src.cache.client import redis_client
from src.menu_management.routers.dish_router import dish_router
from src.menu_management.routers.menu_router import menu_router
from src.menu_management.routers.submenu_router import submenu_router

app = FastAPI(
    title='Menu management',
    version='0.0.2',
    description='Приложение для работы с меню ресторана. Реализует CRUD для трех сущностей: Menu, Submenu, Dish.'
                'Каждый экземпляр Submenu привязывается к Menu, а Dish к Submenu. Вывод данных осуществляется в виде '
                'модели для каждой сущности. При выводе модели Menu, выводится название (title), описание '
                '(description), количество связанных с ним Submenu и общее количество блюд которые входят в это меню, '
                'в полях count. Модель Submenu выводит название, описание и количество блюд. Модель Dish - название,'
                'описание и цену. Цена для блюда всегда выводится с двумя знаками после запятой. При удалении '
                'экземпляра Menu, удаляются все связанные с ним Submenu и Dish. Названия каждой модели внутри '
                'таблицы должно быть уникальным и не может повторяться.'
)

app.include_router(menu_router)
app.include_router(submenu_router)
app.include_router(dish_router)


@app.on_event('shutdown')
async def on_shutdown():
    redis_client.flushdb()
