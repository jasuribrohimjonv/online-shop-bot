from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Order, User
from bot.utils import format_price

router = Router(name="orders")

STATUS_LABELS = {
    "new": "\U0001F195 Yangi",
    "preparing": "\U0001F468\u200D\U0001F373 Tayyorlanmoqda",
    "delivering": "\U0001F69A Yetkazilmoqda",
    "done": "\u2705 Bajarildi",
    "cancelled": "\u274C Bekor qilindi",
}


@router.message(F.text == "\U0001F4E6 Buyurtmalarim")
async def show_orders(message: Message, session: AsyncSession) -> None:
    result = await session.execute(select(User).where(User.telegram_id == message.from_user.id))
    user = result.scalar_one_or_none()
    if user is None:
        await message.answer("Sizda hali buyurtmalar yo'q.")
        return

    result = await session.execute(
        select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc())
    )
    orders = list(result.scalars().all())
    if not orders:
        await message.answer("Sizda hali buyurtmalar yo'q.")
        return

    for order in orders:
        status = STATUS_LABELS.get(order.status, order.status)
        await message.answer(
            f"\U0001F4E6 Buyurtma #{order.id}\n"
            f"Holati: {status}\n"
            f"Summasi: {format_price(order.total_price)}\n"
            f"Sana: {order.created_at.strftime('%Y-%m-%d %H:%M')}"
        )
