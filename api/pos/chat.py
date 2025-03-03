import re
from typing import Annotated

from pydantic import (
    BaseModel,
    computed_field,
    ConfigDict,
    AfterValidator,
    field_serializer,
    field_validator,
)
from pydantic.alias_generators import to_camel
from pytonapi.utils import to_amount, to_nano

from api.pos.base import BaseFDO
from core.dtos.chat import EligibilityCheckType
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


class ChatJettonRuleCPO(BaseModel):
    expected: float | int

    @field_validator("expected")
    @classmethod
    def preprocess_expected(cls, v: float | int) -> float | int:
        if not v:
            return v

        return to_nano(v)


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


class TelegramChatEligibilityRuleFDO(BaseTelegramChatEligibilityRuleFDO):
    actual: float | None = None
    photo_url: str | None = None
    is_eligible: bool = False

    @property
    def expected_human_friendly(self) -> str:
        return human_friendly_number(self.expected)


class TelegramChatWithRulesFDO(BaseModel):
    chat: TelegramChatFDO
    rules: list[TelegramChatEligibilityRuleFDO]
