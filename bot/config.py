from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Config:
    bot_token: str
    admin_ids: list[int]
    database_url: str


def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise RuntimeError(
            "BOT_TOKEN environment variable is not set. "
            "Create a bot with @BotFather and put the token in .env"
        )

    admin_ids_raw = os.getenv("ADMIN_IDS", "")
    admin_ids = [int(x.strip()) for x in admin_ids_raw.split(",") if x.strip()]

    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///shop.db")

    return Config(bot_token=bot_token, admin_ids=admin_ids, database_url=database_url)
