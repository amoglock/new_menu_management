from fastapi import HTTPException
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError

from db import engine
from menu_management.models import Dish
from menu_management.schemas import DishResponse


class DishRepository:

    @classmethod
    async def get_dish_list(cls, submenu_id: str) -> list[DishResponse]:
        stmt = select(Dish).where(Dish.submenu_group == submenu_id)
        try:
            async with engine.connect() as conn:
                result = await conn.execute(stmt)
                return result
        except DBAPIError as e:
            raise HTTPException(status_code=404, detail=f'{e.orig}')

    @classmethod
    async def get_dish(cls, dish_id: str) -> DishResponse:
        stmt = select(Dish).where(Dish.id == dish_id).limit(1)
        try:
            async with engine.connect() as conn:
                dish = await conn.execute(stmt)
                dish = dish.fetchone()
                return dish
        except DBAPIError as e:
            raise HTTPException(status_code=404, detail=f'{e.orig}')

    @classmethod
    async def add_dish(cls, dish_as_dict: dict) -> DishResponse:
        stmt = insert(Dish).values(**dish_as_dict).returning(Dish)
        async with engine.connect() as conn:
            async with conn.begin():
                try:
                    new_dish = await conn.execute(stmt)
                    new_dish = new_dish.fetchone()
                    return new_dish
                except IntegrityError as e:
                    raise HTTPException(status_code=409, detail=f'{e.orig}')
                except DBAPIError as e:
                    raise HTTPException(status_code=404, detail=f'{e.orig}')

    @classmethod
    async def update_dish(cls, dish_id: str, dish: dict) -> DishResponse | dict:
        stmt = update(Dish).where(Dish.id == dish_id).values(dish).returning(Dish)
        try:
            async with engine.connect() as conn:
                async with conn.begin():
                    patched_dish = await conn.execute(stmt)
                    patched_dish = patched_dish.fetchone()
                    return patched_dish
        except IntegrityError as e:
            raise HTTPException(status_code=409, detail=f'{e.orig}')
        except DBAPIError as e:
            raise HTTPException(status_code=404, detail=f'{e.orig}')

    @classmethod
    async def delete_dish(cls, dish_id: str) -> dict[str, bool | str]:
        stmt = delete(Dish).where(Dish.id == dish_id).returning(Dish)
        try:
            async with engine.connect() as conn:
                async with conn.begin():
                    deleted_dish = await conn.execute(stmt)
                    if deleted_dish.fetchone():
                        return {'status': True, 'message': 'The dish has been deleted'}
                    return {'status': False, 'message': 'The dish not found'}
        except DBAPIError as e:
            raise HTTPException(status_code=404, detail=f'{e.orig}')

    @classmethod
    async def count(cls) -> int:
        query = select(func.count()).select_from(Dish)
        async with engine.connect() as conn:
            menu_count = await conn.scalar(query)
            return menu_count
