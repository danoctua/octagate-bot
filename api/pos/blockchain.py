from pydantic import BaseModel, field_validator
from pytonapi.utils import userfriendly_to_raw

from api.pos.base import BaseFDO
from core.dtos.resource import JettonDTO, NftCollectionDTO, NftCollectionAttributeDTO


class JettonFDO(BaseFDO, JettonDTO):
    ...


class GetJettonCPO(BaseFDO):
    whitelisted_only: bool = True


class GetNftCollectionCPO(BaseFDO):
    whitelisted_only: bool = True


class BaseCreateBlockchainItemCPO(BaseModel):
    address: str

    @classmethod
    @field_validator("address", mode="before")
    def validate_address(cls, v: str) -> str:
        if not v:
            raise ValueError("Address is required")

        return userfriendly_to_raw(v)


class CreateJettonCPO(BaseCreateBlockchainItemCPO):
    ...


class BaseUpdateBlockchainItemCPO(BaseFDO):
    is_enabled: bool


class UpdateJettonCPO(BaseUpdateBlockchainItemCPO):
    ...


class NftCollectionAttributeFDO(BaseFDO, NftCollectionAttributeDTO):
    ...


class NftCollectionMetadataFDO(BaseFDO):
    attributes: list[NftCollectionAttributeFDO]


class NftCollectionFDO(BaseFDO, NftCollectionDTO):
    blockchain_metadata: NftCollectionMetadataFDO | None


class CreateNftCollectionCPO(BaseCreateBlockchainItemCPO):
    ...


class UpdateNftCollectionCPO(BaseUpdateBlockchainItemCPO):
    ...
