from sqlalchemy import Select, func

from src.database.db import engine
from src.database.models import Dish, Submenu


async def submenus_counter(menu_id: str) -> int:
    stmt = Select(func.count()).select_from(Submenu).where(Submenu.menu_group == menu_id)
    async with engine.connect() as conn:
        result = await conn.scalar(stmt)
        return result


async def dishes_counter(menu_id: str | None = None, submenu_id: str | None = None) -> int | None:
    if menu_id:
        # query = Select(func.count()).select_from(Dish).filter(Dish.submenu_group == Select(Submenu.id).
        #                                                       where(Submenu.menu_group == 125).scalar_subquery())
        # async with engine.connect() as conn:
        #     result = await conn.scalar(query)
        #     return result
        return 0

    if submenu_id:
        query = Select(func.count()).select_from(Dish).where(Dish.submenu_group == submenu_id)
        async with engine.connect() as conn:
            result = await conn.scalar(query)
            return result
    return None
