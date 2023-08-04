from typing import List

from sqlalchemy import select, insert, update, delete, func

from db import Session
from ..models import Submenu
from ..schemas import SubmenuResponse
from ..utils import dishes_counter


class SubmenuRepository:

    @classmethod
    def get_all_submenus(cls, menu_id: str) -> List[SubmenuResponse]:
        query = select(Submenu).filter_by(menu_group=menu_id)
        with Session() as session:
            submenus = session.execute(query)
            result = submenus.scalars().all()
            result = [SubmenuResponse(id=r.id, title=r.title,
                                      description=r.description,
                                      dishes_count=dishes_counter(submenu_id=r.id)) for r in result]
            return result

    @classmethod
    def get_submenu(cls, submenu_id: str) -> dict:
        try:
            query = select(Submenu.__table__.columns).filter_by(id=submenu_id)
            with Session() as session:
                menus = session.execute(query)
                return menus.mappings().one()
        except Exception:
            return {}

    @classmethod
    def post_submenu(cls, menu_id: str, values: dict) -> SubmenuResponse:
        values["menu_group"] = menu_id
        stmt = insert(Submenu).values(**values).returning(Submenu)
        with Session() as session:
            new_submenu = session.execute(stmt)
            session.commit()
            new_submenu = new_submenu.scalar()
            new_submenu = SubmenuResponse(id=new_submenu.id,
                                          title=new_submenu.title,
                                          description=new_submenu.description,
                                          dishes_count=dishes_counter(submenu_id=new_submenu.id))
            return new_submenu

    @classmethod
    def patch_submenu(cls, submenu_id: str, submenu: dict):
        stmt = update(Submenu).where(Submenu.id == submenu_id).values(submenu).returning(Submenu)
        try:
            with Session() as session:
                patched_submenu = session.execute(stmt)
                session.commit()
                patched_submenu = patched_submenu.scalar()
                patched_submenu = SubmenuResponse(id=patched_submenu.id,
                                                  title=patched_submenu.title,
                                                  description=patched_submenu.description,
                                                  dishes_count=dishes_counter(menu_id=patched_submenu.id)).model_dump()
                return patched_submenu
        except Exception:
            return {}

    @classmethod
    def delete(cls, take_id: str):
        stmt = delete(Submenu).where(Submenu.id == take_id)
        with Session() as session:
            session.execute(stmt)
            session.commit()
        return {"status": True, "message": "The submenu has been deleted"}

    @classmethod
    def count(cls):
        query = select(func.count(Submenu.id)).select_from(Submenu)
        with Session() as session:
            menu_count = session.execute(query)
            session.commit()
            return menu_count.scalar()
