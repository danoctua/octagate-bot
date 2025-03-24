from typing import Self

from pydantic import BaseModel
from telethon.tl.types import User as TelethonUser

from core.settings import core_settings


class TelegramUserDTO(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    is_premium: bool
    language_code: str
    photo_url: str | None = None

    @classmethod
    def from_telethon_user(cls, user: TelethonUser) -> Self:
        return cls(
            id=user.id,
            first_name=user.first_name or "",
            last_name=user.last_name,
            username=user.username,
            is_premium=user.premium or False,
            language_code=user.lang_code or core_settings.default_language,
            photo_url=None,
        )
