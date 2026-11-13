from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.callbacks import CategoryCallback, ProductCallback
from bot.keyboards import categories_keyboard, product_detail_keyboard, products_keyboard
from bot.models import Category, Product
from bot.utils import format_price

router = Router(name="catalog")


@router.message(F.text == "\U0001F6CD Katalog")
async def show_categories(message: Message, session: AsyncSession) -> None:
    result = await session.execute(select(Category).order_by(Category.name))
    categories = list(result.scalars().all())
    if not categories:
        await message.answer("Hozircha kategoriyalar mavjud emas.")
        return
    await message.answer("Kategoriyani tanlang:", reply_markup=categories_keyboard(categories))


@router.callback_query(CategoryCallback.filter())
async def show_products(call: CallbackQuery, callback_data: CategoryCallback, session: AsyncSession) -> None:
    result = await session.execute(
        select(Product).where(Product.category_id == callback_data.id, Product.is_active == True)  # noqa: E712
    )
    products = list(result.scalars().all())
    if not products:
        await call.answer("Bu kategoriyada mahsulot yo'q", show_alert=True)
        return
    await call.message.answer("Mahsulotni tanlang:", reply_markup=products_keyboard(products))
    await call.answer()


@router.callback_query(ProductCallback.filter())
async def show_product_detail(call: CallbackQuery, callback_data: ProductCallback, session: AsyncSession) -> None:
    product = await session.get(Product, callback_data.id)
    if product is None or not product.is_active:
        await call.answer("Mahsulot topilmadi", show_alert=True)
        return

    caption = (
        f"<b>{product.name}</b>\n\n"
        f"{product.description or ''}\n\n"
        f"\U0001F4B0 Narx: {format_price(product.price)}"
    )
    keyboard = product_detail_keyboard(product.id)
    if product.photo_file_id:
        await call.message.answer_photo(product.photo_file_id, caption=caption, reply_markup=keyboard)
    else:
        await call.message.answer(caption, reply_markup=keyboard)
    await call.answer()
