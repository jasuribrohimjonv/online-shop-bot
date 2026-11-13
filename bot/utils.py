from __future__ import annotations

from decimal import Decimal


def format_price(value: Decimal | float | int) -> str:
    amount = float(value)
    formatted = f"{amount:,.0f}".replace(",", " ")
    return f"{formatted} so'm"
