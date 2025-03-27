from pydantic import BaseModel
from pytonapi.utils import raw_to_userfriendly

from core.dtos.chat.rules import EligibilityCheckType, ChatEligibilityRuleDTO
from core.dtos.base import NftItemAttributeDTO
from core.dtos.chat.rules.internal import EligibilitySummaryInternalDTO
from core.models.chat import TelegramChatNFTCollection


class BaseTelegramChatNFTCollectionRuleDTO(BaseModel):
    address: str
    threshold: int
    is_enabled: bool
    required_attributes: list[NftItemAttributeDTO] | None


class CreateTelegramChatNFTCollectionRuleDTO(BaseTelegramChatNFTCollectionRuleDTO):
    chat_id: int


class UpdateTelegramChatNFTCollectionRuleDTO(BaseTelegramChatNFTCollectionRuleDTO):
    ...


class NftEligibilityRuleDTO(ChatEligibilityRuleDTO):
    required_attributes: list[NftItemAttributeDTO] | None

    @classmethod
    def from_nft_collection_rule(cls, nft_collection_rule: TelegramChatNFTCollection):
        return cls(
            id=nft_collection_rule.id,
            category=EligibilityCheckType.NFT_COLLECTION,
            title=nft_collection_rule.nft_collection.name,
            expected=nft_collection_rule.threshold,
            photo_url=nft_collection_rule.nft_collection.logo_path,
            blockchain_address=raw_to_userfriendly(
                nft_collection_rule.nft_collection.address
            ),
            is_enabled=nft_collection_rule.is_enabled,
            required_attributes=[
                NftItemAttributeDTO(
                    trait_type=attribute.trait_type,
                    value=attribute.value,
                )
                for attribute in nft_collection_rule.required_attributes
            ]
            if nft_collection_rule.required_attributes
            else None,
        )


class NftRuleEligibilitySummaryDTO(NftEligibilityRuleDTO):
    actual: float | None = None
    is_eligible: bool = False

    @classmethod
    def from_internal_dto(cls, internal_dto: EligibilitySummaryInternalDTO):
        return cls(
            id=internal_dto.id,
            category=internal_dto.category,
            title=internal_dto.title,
            expected=internal_dto.expected,
            photo_url=None,
            blockchain_address=internal_dto.address,
            is_enabled=internal_dto.is_enabled,
            required_attributes=internal_dto.required_attributes,
            actual=internal_dto.actual,
            is_eligible=internal_dto.is_eligible,  # type: ignore
        )
