from typing import Annotated, Self

from pydantic import BaseModel, Field, field_validator
from pytonapi.utils import userfriendly_to_raw, raw_to_userfriendly

from api.pos.base import BaseFDO
from core.models.blockchain import Jetton


class TonProofDomainPO(BaseModel):
    length_bytes: Annotated[int, Field(alias="lengthBytes")]
    value: str

    class Config:
        extra = "ignore"


class TonProofPO(BaseModel):
    timestamp: int
    domain: TonProofDomainPO
    signature: str
    payload: str


class JettonFDO(BaseFDO):
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


class GetJettonCPO(BaseFDO):
    whitelisted_only: bool = True


class CreateJettonCPO(BaseModel):
    address: str

    @classmethod
    @field_validator("address", mode="before")
    def validate_address(cls, v: str) -> str:
        if not v:
            raise ValueError("Address is required")

        return userfriendly_to_raw(v)


class UpdateJettonCPO(BaseFDO):
    is_enabled: bool
