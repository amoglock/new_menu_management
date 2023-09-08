from fastapi import Depends, HTTPException
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_session
from src.database.models import Menu


class MenuRepository:

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def get_menu_list(self) -> list[Menu]:
        stmt = select(Menu)
        result = await self.session.execute(stmt)
        return list(result.scalars().fetchall())

    async def get_menu(self, menu_id: str) -> Menu:
        stmt = select(Menu).where(Menu.id == menu_id).limit(1)
        try:
            result = await self.session.execute(stmt)
            result = result.scalar()
            return result
        except DBAPIError as e:
            raise HTTPException(status_code=404, detail=f'{e.orig}')

    async def add_new_menu(self, values: dict) -> Menu:
        stmt = insert(Menu).values(**values).returning(Menu)
        try:
            new_menu = await self.session.execute(stmt)
            await self.session.commit()
            new_menu = new_menu.scalar()
            return new_menu
        except IntegrityError:
            raise HTTPException(status_code=409, detail='This menu title already exists')

    async def patch_menu(self, menu_id: str, menu: dict) -> Menu:
        stmt = update(Menu).where(Menu.id == menu_id).values(menu).returning(Menu)
        try:
            new_menu = await self.session.execute(stmt)
            await self.session.commit()
            new_menu = new_menu.scalar()
            return new_menu
        except IntegrityError:
            raise HTTPException(status_code=409, detail='This menu name already exists')
        except DBAPIError as e:
            raise HTTPException(status_code=404, detail=f'{e.orig}')

    async def delete(self, menu_id: str) -> dict[str, bool | str]:
        stmt = delete(Menu).where(Menu.id == menu_id).returning(Menu)
        try:
            deleted_menu = await self.session.execute(stmt)
            await self.session.commit()
            if deleted_menu.fetchone():
                return {'status': True, 'message': 'menu has been deleted'}
            return {'status': False, 'message': 'menu not found'}
        except DBAPIError as e:
            raise HTTPException(status_code=404, detail=f'{e.orig}')

    async def delete_all(self):
        stmt = delete(Menu)
        await self.session.execute(stmt)
        await self.session.commit()
