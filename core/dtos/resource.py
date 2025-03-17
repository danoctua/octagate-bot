from collections import defaultdict
from typing import Self

from pydantic import BaseModel
from pytonapi.schema.nft import NftItem as TONNftItem
from pytonapi.utils import raw_to_userfriendly

from core.dtos.base import (
    NftItemAttributeDTO,
    BaseNftItemMetadataDTO,
    NftCollectionAttributeDTO,
    BaseNftCollectionMetadataDTO,
)
from core.models.blockchain import Jetton, NFTCollection


class NftItemMetadataDTO(BaseNftItemMetadataDTO):
    @classmethod
    def from_nft_item(cls, nft_item: TONNftItem) -> Self:
        return cls(
            attributes=[
                NftItemAttributeDTO(
                    trait_type=trait["trait_type"],
                    value=trait["value"],
                )
                # NFT item could have no attributes
                for trait in nft_item.metadata.get("attributes", [])
            ]
        )


class NftCollectionMetadataDTO(BaseNftCollectionMetadataDTO):
    @classmethod
    def from_items_metadata(cls, items_metadata: list[NftItemMetadataDTO]) -> Self:
        combined = defaultdict(set)
        for item_metadata in items_metadata:
            for attribute in item_metadata.attributes:
                combined[attribute.trait_type].add(attribute.value)

        return cls(
            attributes=[
                NftCollectionAttributeDTO(
                    trait_type=trait_type,
                    values=sorted(values),
                )
                for trait_type, values in combined.items()
            ]
        )


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
    blockchain_metadata: BaseNftCollectionMetadataDTO | None = None

    @classmethod
    def from_orm(cls, obj: NFTCollection) -> Self:
        return cls(
            address=raw_to_userfriendly(obj.address),
            name=obj.name,
            description=obj.description,
            logo_path=obj.logo_path,
            is_enabled=obj.is_enabled,
            blockchain_metadata=obj.blockchain_metadata,
        )
