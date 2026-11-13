from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards import main_menu_keyboard
from bot.models import User

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    result = await session.execute(select(User).where(User.telegram_id == message.from_user.id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            telegram_id=message.from_user.id,
            full_name=message.from_user.full_name or "Noma'lum",
        )
        session.add(user)
        await session.commit()

    await message.answer(
        "Assalomu alaykum! \U0001F44B\n\n"
        "Onlayn do'konimizga xush kelibsiz. Quyidagi menyudan foydalaning:",
        reply_markup=main_menu_keyboard(),
    )


@router.message(F.text == "\u2139\uFE0F Yordam")
async def help_handler(message: Message) -> None:
    await message.answer(
        "\U0001F6CD Katalog \u2014 mahsulotlarni ko'rish\n"
        "\U0001F6D2 Savatcha \u2014 tanlangan mahsulotlar\n"
        "\U0001F4E6 Buyurtmalarim \u2014 buyurtmalar tarixi\n\n"
        "Savolingiz bo'lsa, admin bilan bog'laning."
    )
