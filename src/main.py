from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from menu_management.routers.dish_router import dish_router
from menu_management.routers.menu_router import menu_router
from menu_management.routers.submenu_router import submenu_router

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


@app.on_event('startup')
async def startup():
    redis = aioredis.from_url('redis://localhost', encoding='utf-8', decode_responce=True)
    FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')
