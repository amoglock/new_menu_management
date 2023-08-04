from fastapi import FastAPI

from menu_management.routers.dish_router import dish_router
from menu_management.routers.menu_router import menu_router
from menu_management.routers.submenu_router import submenu_router

app = FastAPI(
    title="Menu management"
)

app.include_router(menu_router)
app.include_router(submenu_router)
app.include_router(dish_router)
