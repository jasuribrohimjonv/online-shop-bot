from __future__ import annotations

from aiogram.filters.callback_data import CallbackData


class CategoryCallback(CallbackData, prefix="cat"):
    id: int


class ProductCallback(CallbackData, prefix="prod"):
    id: int


class CartActionCallback(CallbackData, prefix="cart"):
    action: str  # add, inc, dec, remove, clear, checkout, confirm, cancel
    product_id: int = 0


class AdminProductCallback(CallbackData, prefix="aprod"):
    action: str  # view, edit, delete
    id: int = 0


class OrderStatusCallback(CallbackData, prefix="ordstat"):
    order_id: int
    status: str
