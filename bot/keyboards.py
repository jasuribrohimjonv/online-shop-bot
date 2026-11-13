from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callbacks import (
    AdminProductCallback,
    CartActionCallback,
    CategoryCallback,
    OrderStatusCallback,
    ProductCallback,
)
from bot.models import Category, Product
from bot.utils import format_price


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="\U0001F6CD Katalog"), KeyboardButton(text="\U0001F6D2 Savatcha")],
        [KeyboardButton(text="\U0001F4E6 Buyurtmalarim"), KeyboardButton(text="\u2139\uFE0F Yordam")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def admin_menu_keyboard() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="\u2795 Kategoriya qo'shish"), KeyboardButton(text="\u2795 Mahsulot qo'shish")],
        [KeyboardButton(text="\U0001F4CB Mahsulotlar"), KeyboardButton(text="\U0001F5C2 Buyurtmalar")],
        [KeyboardButton(text="\u2B05\uFE0F Asosiy menyu")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def categories_keyboard(categories: list[Category]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(text=category.name, callback_data=CategoryCallback(id=category.id))
    builder.adjust(2)
    return builder.as_markup()


def products_keyboard(products: list[Product]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.button(
            text=f"{product.name} \u2014 {format_price(product.price)}",
            callback_data=ProductCallback(id=product.id),
        )
    builder.adjust(1)
    return builder.as_markup()


def product_detail_keyboard(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="\U0001F6D2 Savatchaga qo'shish",
        callback_data=CartActionCallback(action="add", product_id=product_id),
    )
    return builder.as_markup()


def cart_item_keyboard(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="\u2796", callback_data=CartActionCallback(action="dec", product_id=product_id))
    builder.button(text="\u2795", callback_data=CartActionCallback(action="inc", product_id=product_id))
    builder.button(text="\u274C", callback_data=CartActionCallback(action="remove", product_id=product_id))
    builder.adjust(3)
    return builder.as_markup()


def cart_checkout_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="\u2705 Buyurtma berish", callback_data=CartActionCallback(action="checkout"))
    builder.button(text="\U0001F5D1 Savatchani tozalash", callback_data=CartActionCallback(action="clear"))
    builder.adjust(1)
    return builder.as_markup()


def confirm_order_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="\u2705 Tasdiqlash", callback_data=CartActionCallback(action="confirm"))
    builder.button(text="\u274C Bekor qilish", callback_data=CartActionCallback(action="cancel"))
    builder.adjust(2)
    return builder.as_markup()


def admin_product_list_keyboard(products: list[Product]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.button(
            text=f"{product.name} ({format_price(product.price)})",
            callback_data=AdminProductCallback(action="view", id=product.id),
        )
    builder.adjust(1)
    return builder.as_markup()


def admin_product_actions_keyboard(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="\u270F\uFE0F Tahrirlash (narx)", callback_data=AdminProductCallback(action="edit", id=product_id))
    builder.button(text="\U0001F5D1 O'chirish", callback_data=AdminProductCallback(action="delete", id=product_id))
    builder.adjust(2)
    return builder.as_markup()


def order_status_keyboard(order_id: int) -> InlineKeyboardMarkup:
    statuses = [
        ("\U0001F195 Yangi", "new"),
        ("\U0001F468\u200D\U0001F373 Tayyorlanmoqda", "preparing"),
        ("\U0001F69A Yetkazilmoqda", "delivering"),
        ("\u2705 Bajarildi", "done"),
        ("\u274C Bekor qilindi", "cancelled"),
    ]
    builder = InlineKeyboardBuilder()
    for text, status in statuses:
        builder.button(text=text, callback_data=OrderStatusCallback(order_id=order_id, status=status))
    builder.adjust(1)
    return builder.as_markup()
