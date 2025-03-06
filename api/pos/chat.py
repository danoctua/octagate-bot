import re
from typing import Annotated, Any, Self

from pydantic import (
    BaseModel,
    computed_field,
    ConfigDict,
    AfterValidator,
    field_serializer,
    field_validator,
)
from pydantic.alias_generators import to_camel
from pytonapi.utils import to_amount, to_nano, raw_to_userfriendly

from api.pos.base import BaseFDO
from core.dtos.chat import EligibilityCheckType
from core.models.chat import TelegramChatJetton, TelegramChatNFTCollection
from core.utils.number import human_friendly_number


PROMOTE_NFT_COLLECTION_TEMPLATE = "https://getgems.io/collection/{collection_address}"
PROMOTE_JETTON_TEMPLATE = (
    "https://app.ston.fi/swap?chartVisible=false&ft=TON&tt={jetton_master_address}"
)

CHAT_INPUT_REGEX = re.compile(
    r"^(?P<chat_id>-?\d+(\.\d+)?)|^(https:\/\/t\.me\/(?P<username>[a-zA-Z0-9_]{4,32}))$"
)


class BaseTelegramChatFDO(BaseFDO):
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


class TelegramChatCPO(BaseModel):
    full: bool = False


class TelegramChatFDO(BaseTelegramChatFDO):
    join_url: str | None = None
    is_member: bool = False
    is_eligible: bool = False


def validate_chat_identifier(v: str) -> str | int:
    match = CHAT_INPUT_REGEX.match(str(v))
    if not match:
        raise ValueError("Invalid chat input: must be chat ID or username")

    if match.group("username"):
        return match.group("username")

    return int(match.group("chat_id"))


class AddChatCPO(BaseModel):
    chat_identifier: Annotated[str | int, AfterValidator(validate_chat_identifier)]

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=False,
    )


class TelegramChatJettonRuleCPO(BaseModel):
    expected: float | int

    @field_validator("expected")
    @classmethod
    def preprocess_expected(cls, v: float | int) -> float | int:
        if not v:
            return v

        return to_nano(v)


class TelegramChatNFTCollectionRuleCPO(BaseModel):
    expected: int


class ToggleChatRuleCPO(BaseFDO):
    is_enabled: bool


class BaseTelegramChatEligibilityRuleFDO(BaseFDO):
    category: EligibilityCheckType
    title: str
    expected: int
    photo_url: str | None
    blockchain_address: str | None
    is_enabled: bool

    @field_serializer("expected", return_type=float | int)
    def preprocess_expected(self, v: int) -> float | int:
        if not v or self.category != EligibilityCheckType.JETTON:
            return v

        return to_amount(v)

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
            category=EligibilityCheckType.JETTON,
            title=jetton_rule.jetton.name,
            expected=jetton_rule.threshold,
            photo_url=jetton_rule.jetton.logo_path,
            blockchain_address=raw_to_userfriendly(jetton_rule.jetton.address),
            is_enabled=jetton_rule.is_enabled,
        )

    @classmethod
    def from_nft_collection_rule(cls, nft_collection_rule: TelegramChatNFTCollection):
        return cls(
            category=EligibilityCheckType.NFT_COLLECTION,
            title=nft_collection_rule.nft_collection.name,
            expected=nft_collection_rule.threshold,
            photo_url=nft_collection_rule.nft_collection.logo_path,
            blockchain_address=raw_to_userfriendly(
                nft_collection_rule.nft_collection.address
            ),
            is_enabled=nft_collection_rule.is_enabled,
        )


class TelegramChatEligibilityRuleFDO(BaseTelegramChatEligibilityRuleFDO):
    actual: float | None = None
    is_eligible: bool = False

    @property
    def expected_human_friendly(self) -> str:
        return human_friendly_number(self.expected)


class TelegramChatWithRulesFDO(BaseModel):
    chat: TelegramChatFDO
    rules: list[TelegramChatEligibilityRuleFDO]
