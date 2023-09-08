from fastapi import Depends, HTTPException
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_session
from src.database.models import Dish


class DishRepository:

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def get_dish_list(self, submenu_id: str) -> list[Dish]:
        stmt = select(Dish).where(Dish.submenu_group == submenu_id)
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().fetchall())
        except DBAPIError as e:
            raise HTTPException(status_code=404, detail=f'{e.orig}')

    async def get_dish(self, dish_id: str) -> Dish:
        stmt = select(Dish).where(Dish.id == dish_id).limit(1)
        try:
            dish = await self.session.execute(stmt)
            dish = dish.scalar()
            return dish
        except DBAPIError as e:
            raise HTTPException(status_code=404, detail=f'{e.orig}')

    async def add_dish(self, dish_as_dict: dict) -> Dish:
        stmt = insert(Dish).values(**dish_as_dict).returning(Dish)
        try:
            new_dish = await self.session.execute(stmt)
            await self.session.commit()
            new_dish = new_dish.scalar()
            return new_dish
        except IntegrityError as e:
            raise HTTPException(status_code=409, detail=f'{e.orig}')
        except DBAPIError as e:
            raise HTTPException(status_code=404, detail=f'{e.orig}')

    async def update_dish(self, dish_id: str, dish: dict) -> Dish:
        stmt = update(Dish).where(Dish.id == dish_id).values(dish).returning(Dish)
        try:
            patched_dish = await self.session.execute(stmt)
            await self.session.commit()
            patched_dish = patched_dish.scalar()
            return patched_dish
        except IntegrityError as e:
            raise HTTPException(status_code=409, detail=f'{e.orig}')
        except DBAPIError as e:
            raise HTTPException(status_code=404, detail=f'{e.orig}')

    async def delete_dish(self, dish_id: str) -> dict[str, bool | str]:
        stmt = delete(Dish).where(Dish.id == dish_id).returning(Dish)
        try:
            deleted_dish = await self.session.execute(stmt)
            await self.session.commit()
            if deleted_dish.scalar():
                return {'status': True, 'message': 'The dish has been deleted'}
            return {'status': False, 'message': 'The dish not found'}
        except DBAPIError as e:
            raise HTTPException(status_code=404, detail=f'{e.orig}')
