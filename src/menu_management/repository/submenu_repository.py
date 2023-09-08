from fastapi import Depends, HTTPException
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_session
from src.database.models import Submenu


class SubmenuRepository:

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def get_list_submenus(self, menu_id: str) -> list[Submenu]:
        stmt = select(Submenu).filter_by(menu_group=menu_id)
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().fetchall())
        except DBAPIError as e:
            raise HTTPException(status_code=404, detail=f'{e.orig}')

    async def get_submenu(self, submenu_id: str) -> Submenu:
        query = select(Submenu).where(Submenu.id == submenu_id)
        try:
            result = await self.session.execute(query)
            result = result.scalar()
            return result
        except DBAPIError as e:
            raise HTTPException(status_code=404, detail=f'{e.orig}')

    async def add_submenu(self, values: dict) -> Submenu:
        stmt = insert(Submenu).values(**values).returning(Submenu)
        try:
            new_submenu = await self.session.execute(stmt)
            await self.session.commit()
            new_submenu = new_submenu.scalar()
            return new_submenu
        except IntegrityError:
            raise HTTPException(status_code=409, detail='This submenu already exists or wrong menu_id')
        except DBAPIError as e:
            raise HTTPException(status_code=404, detail=f'{e.orig}')

    async def update_submenu(self, submenu_id: str, submenu: dict) -> Submenu:
        stmt = update(Submenu).where(Submenu.id == submenu_id).values(submenu).returning(Submenu)
        try:
            new_submenu = await self.session.execute(stmt)
            await self.session.commit()
            new_submenu = new_submenu.scalar()
            return new_submenu
        except DBAPIError as e:
            raise HTTPException(status_code=404, detail=f'{e.orig}')

    async def delete_submenu(self, take_id: str) -> dict[str, str | bool]:
        stmt = delete(Submenu).where(Submenu.id == take_id).returning(Submenu)
        try:
            deleted_submenu = await self.session.execute(stmt)
            await self.session.commit()
            if deleted_submenu.scalar():
                return {'status': True, 'message': 'submenu has been deleted'}
            return {'status': False, 'message': 'submenu not found'}
        except DBAPIError as e:
            raise HTTPException(status_code=404, detail=f'{e.orig}')
