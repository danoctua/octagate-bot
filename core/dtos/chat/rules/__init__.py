import dataclasses
import enum

from pydantic import BaseModel, computed_field
from pytonapi.utils import raw_to_userfriendly

from core.constants import PROMOTE_JETTON_TEMPLATE, PROMOTE_NFT_COLLECTION_TEMPLATE
from core.dtos.chat import TelegramChatDTO
from core.models.chat import TelegramChatJetton, TelegramChatNFTCollection
from core.models.chat import TelegramChatWhitelistExternalSource, TelegramChatWhitelist


class EligibilityCheckType(enum.Enum):
    JETTON = "jetton"
    NFT_COLLECTION = "nft_collection"
    EXTERNAL_SOURCE = "external_source"
    WHITELIST = "whitelist"


@dataclasses.dataclass
class TelegramChatEligibilityRulesDTO:
    jettons: list[TelegramChatJetton]
    nft_collections: list[TelegramChatNFTCollection]
    whitelist_external_sources: list[TelegramChatWhitelistExternalSource]
    whitelist_sources: list[TelegramChatWhitelist]


class ChatEligibilityRuleDTO(BaseModel):
    id: int
    category: EligibilityCheckType
    title: str
    expected: int
    photo_url: str | None = None
    blockchain_address: str | None = None
    is_enabled: bool

    @computed_field
    def promote_url(self) -> str | None:
        if self.category == EligibilityCheckType.JETTON:
            return PROMOTE_JETTON_TEMPLATE.format(
                jetton_master_address=self.blockchain_address
            )
        elif self.category == EligibilityCheckType.NFT_COLLECTION:
            return PROMOTE_NFT_COLLECTION_TEMPLATE.format(
                collection_address=self.blockchain_address
            )
        return None

    @classmethod
    def from_jetton_rule(cls, jetton_rule: TelegramChatJetton):
        return cls(
            id=jetton_rule.id,
            category=EligibilityCheckType.JETTON,
            title=jetton_rule.jetton.symbol,
            expected=jetton_rule.threshold,
            photo_url=jetton_rule.jetton.logo_path,
            blockchain_address=raw_to_userfriendly(jetton_rule.jetton.address),
            is_enabled=jetton_rule.is_enabled,
        )

    @classmethod
    def from_whitelist_external_rule(
        cls, external_rule: TelegramChatWhitelistExternalSource
    ):
        return cls(
            id=external_rule.id,
            category=EligibilityCheckType.EXTERNAL_SOURCE,
            title=external_rule.name,
            expected=1,
            photo_url=None,
            blockchain_address=None,
            is_enabled=external_rule.is_enabled,
        )

    @classmethod
    def from_whitelist_rule(cls, whitelist_rule: TelegramChatWhitelist):
        return cls(
            id=whitelist_rule.id,
            category=EligibilityCheckType.WHITELIST,
            title=whitelist_rule.name,
            expected=1,
            photo_url=None,
            blockchain_address=None,
            is_enabled=whitelist_rule.is_enabled,
        )


class TelegramChatWithRulesDTO(BaseModel):
    chat: TelegramChatDTO
    rules: list[ChatEligibilityRuleDTO]
