from __future__ import annotations

from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.callbacks import AdminProductCallback, CategoryCallback, OrderStatusCallback
from bot.keyboards import (
    admin_menu_keyboard,
    admin_product_actions_keyboard,
    admin_product_list_keyboard,
    categories_keyboard,
    main_menu_keyboard,
    order_status_keyboard,
)
from bot.models import Category, Order, Product
from bot.states import AdminStates
from bot.utils import format_price

router = Router(name="admin")


def register_admin_filters(admin_ids: list[int]) -> None:
    """Restrict every handler in this router to the configured admin Telegram IDs."""
    router.message.filter(F.from_user.id.in_(admin_ids))
    router.callback_query.filter(F.from_user.id.in_(admin_ids))


@router.message(F.text == "/admin")
async def admin_panel(message: Message) -> None:
    await message.answer("\U0001F527 Admin panel", reply_markup=admin_menu_keyboard())


@router.message(F.text == "\u2B05\uFE0F Asosiy menyu")
async def back_to_main(message: Message) -> None:
    await message.answer("Asosiy menyu", reply_markup=main_menu_keyboard())


# ---------- Kategoriya qo'shish ----------


@router.message(F.text == "\u2795 Kategoriya qo'shish")
async def add_category_start(message: Message, state: FSMContext) -> None:
    await message.answer("Yangi kategoriya nomini kiriting:")
    await state.set_state(AdminStates.add_category_name)


@router.message(AdminStates.add_category_name)
async def add_category_finish(message: Message, state: FSMContext, session: AsyncSession) -> None:
    category = Category(name=message.text.strip())
    session.add(category)
    await session.commit()
    await message.answer(f"\u2705 Kategoriya qo'shildi: {category.name}", reply_markup=admin_menu_keyboard())
    await state.clear()


# ---------- Mahsulot qo'shish ----------


@router.message(F.text == "\u2795 Mahsulot qo'shish")
async def add_product_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    result = await session.execute(select(Category).order_by(Category.name))
    categories = list(result.scalars().all())
    if not categories:
        await message.answer("Avval kategoriya qo'shing.")
        return
    await message.answer("Kategoriyani tanlang:", reply_markup=categories_keyboard(categories))
    await state.set_state(AdminStates.add_product_category)


@router.callback_query(AdminStates.add_product_category, CategoryCallback.filter())
async def add_product_category_selected(
    call: CallbackQuery, callback_data: CategoryCallback, state: FSMContext
) -> None:
    await state.update_data(category_id=callback_data.id)
    await call.message.answer("Mahsulot nomini kiriting:")
    await state.set_state(AdminStates.add_product_name)
    await call.answer()


@router.message(AdminStates.add_product_name)
async def add_product_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text.strip())
    await message.answer("Mahsulot tavsifini kiriting (yoki '-' agar kerak bo'lmasa):")
    await state.set_state(AdminStates.add_product_description)


@router.message(AdminStates.add_product_description)
async def add_product_description(message: Message, state: FSMContext) -> None:
    description = None if message.text.strip() == "-" else message.text.strip()
    await state.update_data(description=description)
    await message.answer("Narxini kiriting (faqat raqam, masalan: 150000):")
    await state.set_state(AdminStates.add_product_price)


@router.message(AdminStates.add_product_price)
async def add_product_price(message: Message, state: FSMContext) -> None:
    try:
        price = Decimal(message.text.strip().replace(" ", ""))
    except InvalidOperation:
        await message.answer("Narxni to'g'ri kiriting, masalan: 150000")
        return
    await state.update_data(price=str(price))
    await message.answer("Mahsulot rasmini yuboring (yoki '-' deb yozing, agar rasm bo'lmasa):")
    await state.set_state(AdminStates.add_product_photo)


@router.message(AdminStates.add_product_photo, F.photo)
async def add_product_photo(message: Message, state: FSMContext, session: AsyncSession) -> None:
    photo_file_id = message.photo[-1].file_id
    await _save_product(message, state, session, photo_file_id)


@router.message(AdminStates.add_product_photo, F.text == "-")
async def add_product_no_photo(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await _save_product(message, state, session, None)


async def _save_product(
    message: Message, state: FSMContext, session: AsyncSession, photo_file_id: str | None
) -> None:
    data = await state.get_data()
    product = Product(
        category_id=data["category_id"],
        name=data["name"],
        description=data.get("description"),
        price=Decimal(data["price"]),
        photo_file_id=photo_file_id,
        is_active=True,
    )
    session.add(product)
    await session.commit()
    await message.answer(f"\u2705 Mahsulot qo'shildi: {product.name}", reply_markup=admin_menu_keyboard())
    await state.clear()


# ---------- Mahsulotlarni ko'rish / tahrirlash / o'chirish ----------


@router.message(F.text == "\U0001F4CB Mahsulotlar")
async def list_products(message: Message, session: AsyncSession) -> None:
    result = await session.execute(select(Product).order_by(Product.id.desc()))
    products = list(result.scalars().all())
    if not products:
        await message.answer("Mahsulotlar mavjud emas.")
        return
    await message.answer("Mahsulotlar ro'yxati:", reply_markup=admin_product_list_keyboard(products))


@router.callback_query(AdminProductCallback.filter(F.action == "view"))
async def view_product(call: CallbackQuery, callback_data: AdminProductCallback, session: AsyncSession) -> None:
    product = await session.get(Product, callback_data.id)
    if product is None:
        await call.answer("Topilmadi", show_alert=True)
        return
    text = (
        f"<b>{product.name}</b>\n"
        f"{product.description or ''}\n"
        f"Narx: {format_price(product.price)}\n"
        f"Holati: {'Faol' if product.is_active else 'Faol emas'}"
    )
    await call.message.answer(text, reply_markup=admin_product_actions_keyboard(product.id))
    await call.answer()


@router.callback_query(AdminProductCallback.filter(F.action == "delete"))
async def delete_product(call: CallbackQuery, callback_data: AdminProductCallback, session: AsyncSession) -> None:
    product = await session.get(Product, callback_data.id)
    if product is None:
        await call.answer("Topilmadi", show_alert=True)
        return
    product.is_active = False
    await session.commit()
    await call.message.answer(f"\U0001F5D1 '{product.name}' o'chirildi (nofaol qilindi).")
    await call.answer()


@router.callback_query(AdminProductCallback.filter(F.action == "edit"))
async def edit_product_start(
    call: CallbackQuery, callback_data: AdminProductCallback, state: FSMContext
) -> None:
    await state.update_data(edit_product_id=callback_data.id)
    await call.message.answer("Yangi narxni kiriting (masalan: 150000):")
    await state.set_state(AdminStates.edit_product_value)
    await call.answer()


@router.message(AdminStates.edit_product_value)
async def edit_product_finish(message: Message, state: FSMContext, session: AsyncSession) -> None:
    try:
        price = Decimal(message.text.strip().replace(" ", ""))
    except InvalidOperation:
        await message.answer("Narxni to'g'ri kiriting, masalan: 150000")
        return
    data = await state.get_data()
    product = await session.get(Product, data["edit_product_id"])
    if product is None:
        await message.answer("Mahsulot topilmadi.")
        await state.clear()
        return
    product.price = price
    await session.commit()
    await message.answer(f"\u2705 Narx yangilandi: {format_price(product.price)}", reply_markup=admin_menu_keyboard())
    await state.clear()


# ---------- Buyurtmalar ----------


@router.message(F.text == "\U0001F5C2 Buyurtmalar")
async def list_orders(message: Message, session: AsyncSession) -> None:
    result = await session.execute(select(Order).order_by(Order.created_at.desc()).limit(20))
    orders = list(result.scalars().all())
    if not orders:
        await message.answer("Buyurtmalar yo'q.")
        return
    for order in orders:
        await message.answer(
            f"\U0001F4E6 Buyurtma #{order.id}\n"
            f"Manzil: {order.address}\n"
            f"Telefon: {order.phone}\n"
            f"Summasi: {format_price(order.total_price)}\n"
            f"Holati: {order.status}",
            reply_markup=order_status_keyboard(order.id),
        )


@router.callback_query(OrderStatusCallback.filter())
async def change_order_status(
    call: CallbackQuery, callback_data: OrderStatusCallback, session: AsyncSession
) -> None:
    order = await session.get(Order, callback_data.order_id)
    if order is None:
        await call.answer("Buyurtma topilmadi", show_alert=True)
        return
    order.status = callback_data.status
    await session.commit()
    await call.answer("Holat yangilandi \u2705")
    await call.message.edit_reply_markup(reply_markup=order_status_keyboard(order.id))
