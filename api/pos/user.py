from typing import Any, Self

from api.pos.base import BaseFDO


class UserFDO(BaseFDO):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    is_premium: bool = False
    language_code: str
    photo_url: str | None = None
    wallet_address: str | None

    @classmethod
    def from_orm(cls, obj: Any) -> Self:
        return cls(
            id=obj.id,
            first_name=obj.first_name,
            last_name=obj.last_name,
            username=obj.username,
            is_premium=obj.is_premium,
            language_code=obj.language,
            photo_url=None,
            wallet_address=(obj.wallet.address if obj.wallet else None),
        )


class UpdateUserWalletFDO(BaseFDO):
    user: UserFDO
    task_id: str
