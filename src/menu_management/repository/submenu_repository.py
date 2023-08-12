from fastapi import HTTPException
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError

from db import engine
from menu_management.models import Submenu
from menu_management.schemas import SubmenuResponse


class SubmenuRepository:

    @classmethod
    async def get_list_submenus(cls, menu_id: str) -> list[SubmenuResponse]:
        stmt = select(Submenu).filter_by(menu_group=menu_id)
        try:
            async with engine.connect() as conn:
                result = await conn.execute(stmt)
                return result
        except DBAPIError as e:
            raise HTTPException(status_code=404, detail=f'{e.orig}')

    @classmethod
    async def get_submenu(cls, submenu_id: str):
        query = select(Submenu).where(Submenu.id == submenu_id).limit(1)
        try:
            async with engine.connect() as conn:
                result = await conn.execute(query)
                result = result.fetchone()
                return result
        except DBAPIError as e:
            raise HTTPException(status_code=404, detail=f'{e.orig}')

    @classmethod
    async def add_submenu(cls, values: dict) -> SubmenuResponse:
        stmt = insert(Submenu).values(**values).returning(Submenu)
        async with engine.connect() as conn:
            async with conn.begin():
                try:
                    new_submenu = await conn.execute(stmt)
                    new_submenu = new_submenu.fetchone()
                    return new_submenu
                except IntegrityError:
                    raise HTTPException(status_code=409, detail='This submenu title already exists')
                except DBAPIError as e:
                    raise HTTPException(status_code=404, detail=f'{e.orig}')

    @classmethod
    async def update_submenu(cls, submenu_id: str, submenu: dict) -> SubmenuResponse:
        stmt = update(Submenu).where(Submenu.id == submenu_id).values(submenu).returning(Submenu)
        try:
            async with engine.connect() as conn:
                async with conn.begin():
                    new_submenu = await conn.execute(stmt)
                    new_submenu = new_submenu.fetchone()
                    return new_submenu
        except DBAPIError as e:
            raise HTTPException(status_code=404, detail=f'{e.orig}')

    @classmethod
    async def delete_submenu(cls, take_id: str) -> dict[str, str | bool]:
        stmt = delete(Submenu).where(Submenu.id == take_id).returning(Submenu)
        try:
            async with engine.connect() as conn:
                async with conn.begin():
                    deleted_submenu = await conn.execute(stmt)
                    if deleted_submenu.fetchone():
                        return {'status': True, 'message': 'submenu has been deleted'}
                    return {'status': False, 'message': 'submenu not found'}
        except DBAPIError as e:
            raise HTTPException(status_code=404, detail=f'{e.orig}')

    @classmethod
    async def count(cls) -> int:
        stmt = select(func.count()).select_from(Submenu)
        async with engine.connect() as conn:
            result = await conn.scalar(stmt)
            return result
