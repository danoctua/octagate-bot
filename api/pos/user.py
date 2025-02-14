from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class UserInitDataPO(BaseModel):
    id: int
    username: str
    photo_url: str
    last_name: str
    first_name: str
    language_code: str
    is_premium: bool

    class Config:
        extra = "ignore"


class UserFDO(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    is_premium: bool = False
    language_code: str
    photo_url: str | None = None
    wallet_address: str | None

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
