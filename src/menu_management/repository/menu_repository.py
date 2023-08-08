from sqlalchemy import delete, func, insert, select, update

from db import Session

from ..models import Menu
from ..schemas import MenuResponse
from ..utils import dishes_counter, submenus_counter


class MenuRepository:

    @classmethod
    def get_all_menu(cls) -> list[MenuResponse]:
        with Session() as session:
            result = session.query(Menu).all()
            result = [MenuResponse(id=r.id, title=r.title,
                                   description=r.description,
                                   submenus_count=submenus_counter(r.id),
                                   dishes_count=dishes_counter(menu_id=r.id)) for r in result]
            return result

    @classmethod
    def get_menu(cls, menu_id: str) -> MenuResponse | None:
        try:
            query = select(Menu.__table__.columns).filter_by(id=menu_id)
            with Session() as session:
                menus = session.execute(query)
                return menus.mappings().one()
        except Exception:
            return None

    @classmethod
    def post_menu(cls, values: dict) -> MenuResponse:
        stmt = insert(Menu).values(**values).returning(Menu)
        with Session() as session:
            new_menu = session.execute(stmt)
            session.commit()
            new_menu = new_menu.scalar()
            new_menu = MenuResponse(id=new_menu.id,
                                    title=new_menu.title,
                                    description=new_menu.description,
                                    submenus_count=submenus_counter(new_menu.id),
                                    dishes_count=dishes_counter(menu_id=new_menu.id))
            return new_menu

    @classmethod
    def patch_menu(cls, menu_id: str, menu: dict) -> MenuResponse | dict:
        stmt = update(Menu).where(Menu.id == menu_id).values(menu).returning(Menu)
        try:
            with Session() as session:
                patched_menu = session.execute(stmt)
                session.commit()
                patched_menu = patched_menu.scalar()
                patched_menu = MenuResponse(id=patched_menu.id,
                                            title=patched_menu.title,
                                            description=patched_menu.description,
                                            submenus_count=submenus_counter(patched_menu.id),
                                            dishes_count=dishes_counter(menu_id=patched_menu.id)).model_dump()
                return patched_menu
        except Exception:
            return {}

    @classmethod
    def count(cls) -> int:
        query = select(func.count(Menu.id)).select_from(Menu)
        with Session() as session:
            menu_count = session.execute(query)
            session.commit()
            return menu_count.scalar()

    @classmethod
    def delete(cls, menu_id: str) -> dict[str, bool | str]:
        stmt = delete(Menu).where(Menu.id == menu_id)
        with Session() as session:
            session.execute(stmt)
            session.commit()
        return {'status': True, 'message': 'The menu has been deleted'}

    @classmethod
    def delete_all(cls):
        stmt = delete(Menu)
        with Session() as session:
            session.execute(stmt)
            session.commit()
