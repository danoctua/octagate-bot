from pydantic import BaseModel


class TelegramUserDTO(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    is_premium: bool
    language_code: str
    photo_url: str | None = None
