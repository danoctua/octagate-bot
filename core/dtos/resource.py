from typing import Self

from pydantic import BaseModel
from pytonapi.utils import raw_to_userfriendly

from core.models.blockchain import Jetton, NFTCollection


class JettonDTO(BaseModel):
    address: str
    name: str
    description: str | None
    symbol: str
    logo_path: str | None
    is_enabled: bool

    @classmethod
    def from_orm(cls, obj: Jetton) -> Self:
        return cls(
            address=raw_to_userfriendly(obj.address),
            name=obj.name,
            description=obj.description,
            symbol=obj.symbol,
            logo_path=obj.logo_path,
            is_enabled=obj.is_enabled,
        )


class NftCollectionDTO(BaseModel):
    address: str
    name: str
    description: str | None
    logo_path: str | None
    is_enabled: bool

    @classmethod
    def from_orm(cls, obj: NFTCollection) -> Self:
        return cls(
            address=raw_to_userfriendly(obj.address),
            name=obj.name,
            description=obj.description,
            logo_path=obj.logo_path,
            is_enabled=obj.is_enabled,
        )
