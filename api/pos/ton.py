from typing import Annotated

from pydantic import BaseModel, Field, field_validator
from pytonapi.utils import userfriendly_to_raw

from api.pos.base import BaseFDO


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
