from sqlalchemy import Select, func

from db import Session
from menu_management.models import Submenu, Dish


def submenus_counter(menu_id: str) -> int:
    query = Select(func.count()).select_from(Submenu).where(Submenu.menu_group == menu_id)
    with Session() as session:
        result = session.scalar(query)
        return result


def dishes_counter(menu_id: str = None, submenu_id: str = None) -> int:
    if menu_id:
        query = Select(func.count()).select_from(Dish).filter(Dish.submenu_group == Select(Submenu.id).
                                                              where(Submenu.menu_group == menu_id).scalar_subquery())
        with Session() as session:
            result = session.scalar(query)
            return result
    if submenu_id:
        query = Select(func.count()).select_from(Dish).where(Dish.submenu_group == submenu_id)
        with Session() as session:
            result = session.scalar(query)
            return result
