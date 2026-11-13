from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    waiting_for_address = State()
    waiting_for_phone = State()
    confirm = State()


class AdminStates(StatesGroup):
    add_category_name = State()

    add_product_category = State()
    add_product_name = State()
    add_product_description = State()
    add_product_price = State()
    add_product_photo = State()

    edit_product_value = State()
