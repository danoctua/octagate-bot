from pydantic import BaseModel


class TelegramUserDTO(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    is_premium: bool
    language_code: str
