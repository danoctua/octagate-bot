import dataclasses
import datetime
import enum
from functools import cached_property
from typing import Self, Any

from pydantic import BaseModel, computed_field
from pytonapi.utils import raw_to_userfriendly

from core.models.chat import (
    TelegramChatJetton,
    TelegramChatNFTCollection,
    TelegramChatWhitelistExternalSource,
    TelegramChatWhitelist,
)
from core.utils.number import human_friendly_number


PROMOTE_NFT_COLLECTION_TEMPLATE = "https://getgems.io/collection/{collection_address}"
PROMOTE_JETTON_TEMPLATE = (
    "https://app.ston.fi/swap?chartVisible=false&ft=TON&tt={jetton_master_address}"
)


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


class TelegramChatEligibilityItemDTO(BaseModel):
    id: int
    category: EligibilityCheckType
    title: str
    address_raw: str | None = None  # required for blockchain rules only
    current: float | int = 0.0
    expected: float | int
    is_enabled: bool

    @property
    def address(self):
        if not self.address_raw:
            return None
        return raw_to_userfriendly(self.address_raw)

    @property
    def is_eligible(self):
        return self.current >= self.expected

    @property
    def current_human_friendly(self) -> str:
        # TODO deprecate
        return human_friendly_number(self.current)

    @property
    def expected_human_friendly(self) -> str:
        return human_friendly_number(self.expected)

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} "
            f"{self.category=} "
            f"{self.title=} "
            f"{self.address=} "
            f"{self.current=} "
            f"{self.expected=}>"
        )


class TelegramChatEligibilitySummaryDTO(BaseModel):
    items: list[TelegramChatEligibilityItemDTO]
    is_admin: bool

    def __bool__(self):
        return self.is_admin or any(item.is_eligible for item in self.items)

    def __repr__(self):
        return f"<{self.__class__.__name__} ({self.items=}) {self.is_admin=}>"


class CreateTelegramChatJettonRuleDTO(BaseModel):
    chat_id: int
    address: str
    threshold: int
    is_enabled: bool


class CreateTelegramChatNFTCollectionRuleDTO(BaseModel):
    chat_id: int
    address: str
    threshold: int
    is_enabled: bool


class TelegramChatWhitelistDifferenceDTO(BaseModel):
    previous: list[int] | None
    current: list[int]

    @cached_property
    def removed(self) -> list[int]:
        if not self.previous:
            return []
        return list(set(self.previous) - set(self.current))

    @cached_property
    def added(self) -> list[int]:
        if not self.previous:
            return self.current
        return list(set(self.current) - set(self.previous))


class BaseTelegramChatEligibilityRuleDTO(BaseModel):
    id: int
    category: EligibilityCheckType
    title: str
    expected: int
    photo_url: str | None
    blockchain_address: str | None
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


class TelegramChatWhitelistCPO(BaseModel):
    users: list[int]


class BaseTelegramChatWhitelistDTO(BaseModel):
    id: int
    chat_id: int
    name: str
    description: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    is_enabled: bool
    users: list[int] | None = None


class TelegramChatWhitelistDTO(BaseTelegramChatWhitelistDTO):
    @classmethod
    def from_orm(cls, obj: TelegramChatWhitelist) -> Self:
        return cls(
            id=obj.id,
            chat_id=obj.chat_id,
            name=obj.name,
            description=obj.description,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            is_enabled=obj.is_enabled,
            users=obj.content,
        )


class TelegramChatWhitelistExternalSourceDTO(BaseTelegramChatWhitelistDTO):
    url: str

    @classmethod
    def from_orm(cls, obj: TelegramChatWhitelistExternalSource) -> Self:
        return cls(
            id=obj.id,
            chat_id=obj.chat_id,
            url=obj.url,
            name=obj.name,
            description=obj.description,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            is_enabled=obj.is_enabled,
            users=obj.content,
        )


class BaseTelegramChatDTO(BaseModel):
    id: int
    username: str | None
    title: str
    description: str | None
    slug: str
    is_forum: bool
    logo_path: str | None

    @classmethod
    def from_orm(cls, obj: Any) -> Self:
        return cls(
            id=obj.id,
            username=obj.username,
            title=obj.title,
            description=obj.description,
            slug=obj.slug,
            is_forum=obj.is_forum,
            logo_path=obj.logo_path,
        )


class TelegramChatDTO(BaseTelegramChatDTO):
    join_url: str | None = None
    is_member: bool = False
    is_eligible: bool = False


class TelegramChatEligibilityRuleDTO(BaseTelegramChatEligibilityRuleDTO):
    actual: float | None = None
    is_eligible: bool = False


class TelegramChatWithRulesDTO(BaseModel):
    chat: TelegramChatDTO
    rules: list[TelegramChatEligibilityRuleDTO]
