import dataclasses
import enum

from pydantic import BaseModel, computed_field

from core.constants import PROMOTE_JETTON_TEMPLATE, PROMOTE_NFT_COLLECTION_TEMPLATE
from core.dtos.chat import TelegramChatDTO
from core.models.chat import (
    TelegramChatJetton,
    TelegramChatNFTCollection,
    TelegramChatToncoin,
)
from core.models.chat import TelegramChatWhitelistExternalSource, TelegramChatWhitelist


class EligibilityCheckType(enum.Enum):
    TONCOIN = "toncoin"
    JETTON = "jetton"
    NFT_COLLECTION = "nft_collection"
    EXTERNAL_SOURCE = "external_source"
    WHITELIST = "whitelist"


@dataclasses.dataclass
class TelegramChatEligibilityRulesDTO:
    toncoin: list[TelegramChatToncoin]
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
        if not self.blockchain_address:
            return None

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
    def from_toncoin_rule(cls, rule: TelegramChatToncoin):
        return cls(
            id=rule.id,
            category=EligibilityCheckType.TONCOIN,
            title="TON",
            expected=rule.threshold,
            photo_url="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTYiIGhlaWdodD0iNTYiIHZpZXdCb3g9IjAgMCA1NiA1NiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTI4IDU2QzQzLjQ2NCA1NiA1NiA0My40NjQgNTYgMjhDNTYgMTIuNTM2IDQzLjQ2NCAwIDI4IDBDMTIuNTM2IDAgMCAxMi41MzYgMCAyOEMwIDQzLjQ2NCAxMi41MzYgNTYgMjggNTZaIiBmaWxsPSIjMDA5OEVBIi8+CjxwYXRoIGQ9Ik0zNy41NjAzIDE1LjYyNzdIMTguNDM4NkMxNC45MjI4IDE1LjYyNzcgMTIuNjk0NCAxOS40MjAyIDE0LjQ2MzIgMjIuNDg2MUwyNi4yNjQ0IDQyLjk0MDlDMjcuMDM0NSA0NC4yNzY1IDI4Ljk2NDQgNDQuMjc2NSAyOS43MzQ1IDQyLjk0MDlMNDEuNTM4MSAyMi40ODYxQzQzLjMwNDUgMTkuNDI1MSA0MS4wNzYxIDE1LjYyNzcgMzcuNTYyNyAxNS42Mjc3SDM3LjU2MDNaTTI2LjI1NDggMzYuODA2OEwyMy42ODQ3IDMxLjgzMjdMMTcuNDgzMyAyMC43NDE0QzE3LjA3NDIgMjAuMDMxNSAxNy41Nzk1IDE5LjEyMTggMTguNDM2MiAxOS4xMjE4SDI2LjI1MjRWMzYuODA5MkwyNi4yNTQ4IDM2LjgwNjhaTTM4LjUxMDggMjAuNzM5TDMyLjMxMTggMzEuODM1MUwyOS43NDE3IDM2LjgwNjhWMTkuMTE5NEgzNy41NTc5QzM4LjQxNDYgMTkuMTE5NCAzOC45MTk5IDIwLjAyOTEgMzguNTEwOCAyMC43MzlaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K",
            blockchain_address=None,
            is_enabled=rule.is_enabled,
        )

    @classmethod
    def from_jetton_rule(cls, jetton_rule: TelegramChatJetton):
        return cls(
            id=jetton_rule.id,
            category=EligibilityCheckType.JETTON,
            title=jetton_rule.jetton.symbol,
            expected=jetton_rule.threshold,
            photo_url=jetton_rule.jetton.logo_path,
            blockchain_address=jetton_rule.jetton.address,
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
