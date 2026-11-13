from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.callbacks import CartActionCallback
from bot.keyboards import (
    cart_checkout_keyboard,
    cart_item_keyboard,
    confirm_order_keyboard,
    main_menu_keyboard,
)
from bot.models import CartItem, Order, OrderItem, Product, User
from bot.states import OrderStates
from bot.utils import format_price

router = Router(name="cart")


async def _get_or_create_user(session: AsyncSession, telegram_id: int, full_name: str) -> User:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(telegram_id=telegram_id, full_name=full_name)
        session.add(user)
        await session.commit()
    return user


@router.callback_query(CartActionCallback.filter(F.action == "add"))
async def add_to_cart(call: CallbackQuery, callback_data: CartActionCallback, session: AsyncSession) -> None:
    user = await _get_or_create_user(session, call.from_user.id, call.from_user.full_name or "Noma'lum")

    result = await session.execute(
        select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == callback_data.product_id)
    )
    item = result.scalar_one_or_none()
    if item is None:
        item = CartItem(user_id=user.id, product_id=callback_data.product_id, quantity=1)
        session.add(item)
    else:
        item.quantity += 1
    await session.commit()
    await call.answer("Savatchaga qo'shildi \u2705")


async def _render_cart(session: AsyncSession, user: User, message: Message) -> None:
    result = await session.execute(select(CartItem).where(CartItem.user_id == user.id))
    items = list(result.scalars().all())
    if not items:
        await message.answer("Savatchangiz bo'sh \U0001F6D2", reply_markup=main_menu_keyboard())
        return

    total = 0
    await message.answer("\U0001F6D2 <b>Sizning savatchangiz:</b>")
    for item in items:
        product = await session.get(Product, item.product_id)
        subtotal = product.price * item.quantity
        total += subtotal
        text = f"{product.name}\n{item.quantity} x {format_price(product.price)} = {format_price(subtotal)}"
        await message.answer(text, reply_markup=cart_item_keyboard(product.id))

    await message.answer(f"\U0001F4B0 Jami: {format_price(total)}", reply_markup=cart_checkout_keyboard())


@router.message(F.text == "\U0001F6D2 Savatcha")
async def show_cart(message: Message, session: AsyncSession) -> None:
    user = await _get_or_create_user(session, message.from_user.id, message.from_user.full_name or "Noma'lum")
    await _render_cart(session, user, message)


@router.callback_query(CartActionCallback.filter(F.action.in_({"inc", "dec", "remove"})))
async def update_cart_item(call: CallbackQuery, callback_data: CartActionCallback, session: AsyncSession) -> None:
    user = await _get_or_create_user(session, call.from_user.id, call.from_user.full_name or "Noma'lum")
    result = await session.execute(
        select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == callback_data.product_id)
    )
    item = result.scalar_one_or_none()
    if item is None:
        await call.answer("Mahsulot savatchada topilmadi", show_alert=True)
        return

    if callback_data.action == "inc":
        item.quantity += 1
        await session.commit()
        await call.answer("Miqdor oshirildi")
    elif callback_data.action == "dec":
        item.quantity -= 1
        if item.quantity <= 0:
            await session.delete(item)
        await session.commit()
        await call.answer("Miqdor kamaytirildi")
    elif callback_data.action == "remove":
        await session.delete(item)
        await session.commit()
        await call.answer("Mahsulot savatchadan o'chirildi")

    await call.message.delete()


@router.callback_query(CartActionCallback.filter(F.action == "clear"))
async def clear_cart(call: CallbackQuery, session: AsyncSession) -> None:
    user = await _get_or_create_user(session, call.from_user.id, call.from_user.full_name or "Noma'lum")
    result = await session.execute(select(CartItem).where(CartItem.user_id == user.id))
    for item in result.scalars().all():
        await session.delete(item)
    await session.commit()
    await call.message.answer("Savatcha tozalandi \U0001F5D1", reply_markup=main_menu_keyboard())
    await call.answer()


@router.callback_query(CartActionCallback.filter(F.action == "checkout"))
async def start_checkout(call: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    user = await _get_or_create_user(session, call.from_user.id, call.from_user.full_name or "Noma'lum")
    result = await session.execute(select(CartItem).where(CartItem.user_id == user.id))
    items = list(result.scalars().all())
    if not items:
        await call.answer("Savatcha bo'sh", show_alert=True)
        return

    await call.message.answer("\U0001F4CD Yetkazib berish manzilingizni kiriting:")
    await state.set_state(OrderStates.waiting_for_address)
    await call.answer()


@router.message(OrderStates.waiting_for_address)
async def process_address(message: Message, state: FSMContext) -> None:
    await state.update_data(address=message.text)
    await message.answer("\U0001F4DE Telefon raqamingizni kiriting (masalan: +998901234567):")
    await state.set_state(OrderStates.waiting_for_phone)


@router.message(OrderStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.update_data(phone=message.text)
    data = await state.get_data()

    user = await _get_or_create_user(session, message.from_user.id, message.from_user.full_name or "Noma'lum")
    result = await session.execute(select(CartItem).where(CartItem.user_id == user.id))
    items = list(result.scalars().all())

    total = 0
    lines = []
    for item in items:
        product = await session.get(Product, item.product_id)
        subtotal = product.price * item.quantity
        total += subtotal
        lines.append(f"{product.name} x{item.quantity} = {format_price(subtotal)}")

    summary = (
        "\U0001F9FE <b>Buyurtma tafsilotlari:</b>\n\n"
        + "\n".join(lines)
        + f"\n\n\U0001F4B0 Jami: {format_price(total)}"
        + f"\n\U0001F4CD Manzil: {data['address']}"
        + f"\n\U0001F4DE Telefon: {data['phone']}"
    )
    await message.answer(summary, reply_markup=confirm_order_keyboard())
    await state.set_state(OrderStates.confirm)


@router.callback_query(OrderStates.confirm, CartActionCallback.filter(F.action == "confirm"))
async def confirm_order(
    call: CallbackQuery, state: FSMContext, session: AsyncSession, admin_ids: list[int]
) -> None:
    data = await state.get_data()
    user = await _get_or_create_user(session, call.from_user.id, call.from_user.full_name or "Noma'lum")
    result = await session.execute(select(CartItem).where(CartItem.user_id == user.id))
    items = list(result.scalars().all())
    if not items:
        await call.answer("Savatcha bo'sh", show_alert=True)
        await state.clear()
        return

    total = 0
    order = Order(
        user_id=user.id,
        status="new",
        address=data["address"],
        phone=data["phone"],
        total_price=0,
    )
    session.add(order)
    await session.flush()

    for item in items:
        product = await session.get(Product, item.product_id)
        subtotal = product.price * item.quantity
        total += subtotal
        session.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                price=product.price,
                quantity=item.quantity,
            )
        )
        await session.delete(item)

    order.total_price = total
    await session.commit()

    await call.message.answer(
        f"\u2705 Buyurtmangiz qabul qilindi! Buyurtma raqami: #{order.id}\n"
        "Tez orada siz bilan bog'lanamiz.",
        reply_markup=main_menu_keyboard(),
    )
    await state.clear()

    bot = call.bot
    for admin_id in admin_ids:
        try:
            await bot.send_message(
                admin_id,
                f"\U0001F195 Yangi buyurtma #{order.id}\n"
                f"Mijoz: {user.full_name} (id: {user.telegram_id})\n"
                f"Manzil: {order.address}\n"
                f"Telefon: {order.phone}\n"
                f"Summasi: {format_price(order.total_price)}",
            )
        except Exception:
            pass

    await call.answer()


@router.callback_query(OrderStates.confirm, CartActionCallback.filter(F.action == "cancel"))
async def cancel_order(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer("Buyurtma bekor qilindi.", reply_markup=main_menu_keyboard())
    await call.answer()
