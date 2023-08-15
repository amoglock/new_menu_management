# from fastapi import HTTPException
#
# from src.menu_management.schemas import CreateDish, CreateMenu, CreateSubmenu
# from src.menu_management.sevices.dish_service import DishService
# from src.menu_management.sevices.menu_service import MenuService
# from src.menu_management.sevices.submenu_servise import SubmenuService
#
#
# class TestCrud:
#
#     menu_id: str
#     submenu_id: str
#     dishes_id: list[str]
#
#     @classmethod
#     def test_add_menu(cls):
#         """Add a menu"""
#
#         menu = CreateMenu(title='my_menu', description='my_menu_description')
#         menu = MenuService.post_menu(menu)
#         assert menu.id
#         assert MenuService.count() == 1
#         assert menu.submenus_count == 0
#         assert menu.dishes_count == 0
#         cls.menu_id = str(menu.id)
#
#     @classmethod
#     def test_add_submenu(cls):
#         """Add a submenu"""
#
#         submenu = CreateSubmenu(title='my_submenu', description='my_submenu_description')
#         submenu = SubmenuService.post_submenu(cls.menu_id, submenu)
#         assert submenu
#         assert SubmenuService.count() == 1
#         assert submenu.dishes_count == 0
#         cls.submenu_id = str(submenu.id)
#         added_submenu = SubmenuService.get_submenu(cls.submenu_id)
#         assert added_submenu.dishes_count == 0
#         added_menu = MenuService.get_menu(cls.menu_id)
#         assert added_menu['submenus_count'] == 1
#         assert added_menu['dishes_count'] == 0
#
#     @classmethod
#     def test_add_two_dish(cls):
#         """Add two dishes to table. Checks the price is rounded to two decimal places"""
#
#         dishes = [
#             CreateDish(title='my_dish', description='my_dish', price='15.25621'),
#             CreateDish(title='my_dish2', description='my_dish2', price='4'),
#         ]
#
#         for dish in dishes:
#             new_dish = DishService.post_dish(cls.submenu_id, cls.menu_id, dish)
#             price_field = new_dish.price.split('.')[1]
#             assert len(price_field) == 2
#         assert DishService.count() == 2
#         dishes = DishService.get_all_dishes(cls.submenu_id)
#         cls.dishes_id = [str(dish.id) for dish in dishes]
#
#     @classmethod
#     def test_check_menu(cls):
#         """Checks counter a submenu and dish for the menu model"""
#
#         menu = MenuService.get_menu(cls.menu_id)
#         assert menu['submenus_count'] == 1
#         assert menu['dishes_count'] == 2
#
#     @classmethod
#     def test_check_submenu(cls):
#         """Checks counter a dish and dish for the submenu model"""
#
#         submenu = SubmenuService.get_submenu(cls.submenu_id)
#         assert submenu.get('dishes_count') == 2
#
#     @classmethod
#     def test_delete_submenu(cls):
#         """Checks correct deleting"""
#
#         SubmenuService.delete(cls.submenu_id, cls.menu_id)
#         assert SubmenuService.count() == 0
#
#     @classmethod
#     def test_check_list(cls):
#         """Check after deleting the submenu the dishes associated with it are also deleted"""
#
#         submenu = SubmenuService.get_all_submenus(cls.menu_id)
#         dish = DishService.get_all_dishes(cls.submenu_id)
#         assert submenu == []
#         assert dish == []
#
#     @classmethod
#     def test_menu_counter(cls):
#         """Checks counter a submenu and dish for the menu model"""
#
#         menu = MenuService.get_menu(cls.menu_id)
#         assert menu.get('submenus_count') == 0
#         assert menu.get('dishes_count') == 0
#
#     @classmethod
#     def test_delete_menu(cls):
#         """Deletes the menu. Checks the Exception after call deleted menu"""
#
#         try:
#             MenuService.delete(cls.menu_id)
#             MenuService.get_menu(cls.menu_id)
#         except HTTPException as ex:
#             assert ex.status_code == 404
#             assert ex.detail == 'menu not found'
#
#     @classmethod
#     def get_all_menu(cls):
#         """Base is empty"""
#
#         menu = MenuService.get_all_menu()
#         assert menu == []
