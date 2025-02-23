from typing import Annotated

from pydantic import BaseModel, Field

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
