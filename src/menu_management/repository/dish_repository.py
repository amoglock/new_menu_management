from typing import List

from db import Session
from sqlalchemy import insert, select, update, delete, func

from ..models import Dish
from ..schemas import DishResponse


class DishRepository:

    @classmethod
    def get_all_dishes(cls, submenu_id: str) -> List[DishResponse]:
        query = select(Dish).filter_by(submenu_group=submenu_id)
        with Session() as session:
            dishes = session.execute(query)
            result = dishes.scalars().all()
            result = [DishResponse(id=dish.id, title=dish.title,
                                   description=dish.description,
                                   price=dish.price) for dish in result]
            return result

    @classmethod
    def get_dish(cls, dish_id: str) -> dict:
        try:
            query = select(Dish.__table__.columns).filter_by(id=dish_id)
            with Session() as session:
                menus = session.execute(query)
                return menus.mappings().one()
        except Exception:
            return {}

    @classmethod
    def post_dish(cls, submenu_id: str, values: dict) -> DishResponse:
        values["submenu_group"] = submenu_id
        values["price"] = str("{:.2f}".format(float(values.get("price"))))
        stmt = insert(Dish).values(**values).returning(Dish)
        with Session() as session:
            new_dish = session.execute(stmt)
            session.commit()
            new_dish = new_dish.scalar()
            new_dish = DishResponse(id=new_dish.id,
                                    title=new_dish.title,
                                    description=new_dish.description,
                                    price=new_dish.price)
            return new_dish

    @classmethod
    def patch_dish(cls, dish_id: str, dish: dict):
        stmt = update(Dish).where(Dish.id == dish_id).values(dish).returning(Dish)
        try:
            with Session() as session:
                patched_dish = session.execute(stmt)
                session.commit()
                patched_dish = patched_dish.scalar()
                patched_dish = DishResponse(id=patched_dish.id,
                                            title=patched_dish.title,
                                            description=patched_dish.description,
                                            price=str("{:.2f}".format(float(patched_dish.price)))).model_dump()
                return patched_dish
        except Exception:
            return {}

    @classmethod
    def delete(cls, take_id: str):
        stmt = delete(Dish).where(Dish.id == take_id)
        with Session() as session:
            session.execute(stmt)
            session.commit()
        return {"status": True, "message": "The dish has been deleted"}

    @classmethod
    def count(cls):
        query = select(func.count(Dish.id)).select_from(Dish)
        with Session() as session:
            menu_count = session.execute(query)
            session.commit()
            return menu_count.scalar()
