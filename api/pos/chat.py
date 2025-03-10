import re
from typing import Annotated, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    AfterValidator,
    field_validator,
    field_serializer,
    Field,
)
from pydantic.alias_generators import to_camel
from pytonapi.utils import to_nano, userfriendly_to_raw, to_amount

from api.pos.base import BaseFDO
from core.dtos.chat import (
    BaseTelegramChatEligibilityRuleDTO,
    EligibilityCheckType,
    BaseTelegramChatDTO,
    TelegramChatDTO,
    TelegramChatWithRulesDTO,
    TelegramChatEligibilityRuleDTO,
    TelegramChatWhitelistDTO,
    TelegramChatWhitelistExternalSourceDTO,
)

CHAT_INPUT_REGEX = re.compile(
    r"^(?P<chat_id>-?\d+(\.\d+)?)|^(https:\/\/t\.me\/(?P<username>[a-zA-Z0-9_]{4,32}))$"
)


class BaseTelegramChatFDO(BaseFDO, BaseTelegramChatDTO):
    ...


class TelegramChatCPO(BaseModel):
    full: bool = False


class TelegramChatFDO(BaseFDO, TelegramChatDTO):
    ...


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


class BaseTelegramChatRuleCPO(BaseFDO):
    address: str
    expected: float | int
    is_enabled: bool = True

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        return userfriendly_to_raw(v)


class TelegramChatJettonRuleCPO(BaseTelegramChatRuleCPO):
    @field_validator("expected")
    @classmethod
    def preprocess_expected(cls, v: float | int) -> float | int:
        if not v:
            return v

        return to_nano(v)


class TelegramChatNFTCollectionRuleCPO(BaseTelegramChatRuleCPO):
    ...


class BaseTelegramChatEligibilityRuleFDO(BaseFDO, BaseTelegramChatEligibilityRuleDTO):
    @field_serializer("expected", return_type=float | int)
    def preprocess_expected(self, v: int) -> float | int:
        if not v or self.category != EligibilityCheckType.JETTON:
            return v

        return to_amount(v)


class TelegramChatWithRulesFDO(BaseFDO):
    chat: BaseTelegramChatFDO
    rules: list[BaseTelegramChatEligibilityRuleFDO]

    @classmethod
    def from_dto(cls, dto: TelegramChatWithRulesDTO) -> Self:
        return cls(
            chat=BaseTelegramChatFDO.model_validate(dto.chat.model_dump()),
            rules=[
                BaseTelegramChatEligibilityRuleFDO.model_validate(rule.model_dump())
                for rule in dto.rules
            ],
        )


class TelegramChatEligibilityRuleFDO(BaseFDO, TelegramChatEligibilityRuleDTO):
    ...


class TelegramChatWithEligibilityRulesFDO(BaseFDO):
    """
    Chat with eligibility rules. Returns not only chat and rules data,
    but whether user is eligible for chat
    """

    chat: TelegramChatFDO
    rules: list[TelegramChatEligibilityRuleFDO]

    @classmethod
    def from_dto(cls, dto: TelegramChatWithRulesDTO) -> Self:
        return cls(
            chat=TelegramChatFDO.model_validate(dto.chat.model_dump()),
            rules=[
                TelegramChatEligibilityRuleFDO.model_validate(rule.model_dump())
                for rule in dto.rules
            ],
        )


class CreateTelegramChatWhitelistCPO(BaseFDO):
    name: Annotated[str, Field(min_length=1, max_length=255)]
    description: Annotated[str | None, Field(min_length=0, max_length=255)] = None
    users: list[int]


class UpdateTelegramChatWhitelistCPO(CreateTelegramChatWhitelistCPO):
    is_enabled: bool


class TelegramChatWhitelistFDO(BaseFDO, TelegramChatWhitelistDTO):
    ...


class TelegramChatWhitelistExternalSourceFDO(
    BaseFDO, TelegramChatWhitelistExternalSourceDTO
):
    ...
