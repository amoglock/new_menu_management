from fastapi import HTTPException
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db import engine
from menu_management.models import Menu
from menu_management.schemas import MenuResponse


class MenuRepository:

    @classmethod
    async def get_menu_list(cls) -> list[MenuResponse]:
        stmt = select(Menu)
        async with engine.connect() as conn:
            result = await conn.execute(stmt)
            return result

    @classmethod
    async def get_menu(cls, menu_id: str) -> MenuResponse:
        stmt = select(Menu).where(Menu.id == menu_id)
        try:
            async with engine.connect() as conn:
                result = await conn.execute(stmt)
                result = result.fetchone()
                return result
        except SQLAlchemyError as e:
            print('Error:', e.args)

    @classmethod
    async def add_new_menu(cls, values: dict) -> MenuResponse:
        stmt = insert(Menu).values(**values).returning(Menu)
        async with engine.connect() as conn:
            async with conn.begin():
                try:
                    new_menu = await conn.execute(stmt)
                    new_menu = new_menu.fetchone()
                    return new_menu
                except IntegrityError:
                    raise HTTPException(status_code=409, detail='This menu name already exists')

    @classmethod
    async def patch_menu(cls, menu_id: str, menu: dict) -> MenuResponse:
        stmt = update(Menu).where(Menu.id == menu_id).values(menu).returning(Menu)
        try:
            async with engine.connect() as conn:
                async with conn.begin():
                    new_menu = await conn.execute(stmt)
                    new_menu = new_menu.fetchone()
                    return new_menu
        except IntegrityError:
            raise HTTPException(status_code=409, detail='This menu name already exists')
        except SQLAlchemyError as e:
            print('Error:', e.args)

    @classmethod
    async def delete(cls, menu_id: str) -> dict[str, bool | str]:
        stmt = delete(Menu).where(Menu.id == menu_id).returning(Menu)
        try:
            async with engine.connect() as conn:
                async with conn.begin():
                    deleted_menu = await conn.execute(stmt)
                    if deleted_menu.fetchone():
                        return {'status': True, 'message': 'The menu has been deleted'}
                    return {}
        except SQLAlchemyError as e:
            return {'status': False, 'message': e.args}

    @classmethod
    async def count(cls) -> int:
        stmt = select(func.count()).select_from(Menu)
        async with engine.connect() as conn:
            result = await conn.scalar(stmt)
            return result

    @classmethod
    async def delete_all(cls):
        stmt = delete(Menu)
        async with engine.connect() as conn:
            async with conn.begin():
                conn.execute(stmt)
