import re
from typing import Annotated, Self

from pydantic import (
    BaseModel,
    AfterValidator,
    field_validator,
    field_serializer,
    Field,
    AnyHttpUrl,
)
from pytonapi.utils import to_nano, userfriendly_to_raw, to_amount

from api.pos.base import BaseFDO
from core.dtos.chat import (
    BaseTelegramChatDTO,
    TelegramChatDTO,
)
from core.dtos.chat.rules import (
    EligibilityCheckType,
    ChatEligibilityRuleDTO,
    TelegramChatWithRulesDTO,
)
from core.dtos.chat.rules.summary import (
    RuleEligibilitySummaryDTO,
    TelegramChatWithEligibilitySummaryDTO,
)
from core.dtos.chat.rules.whitelist import WhitelistRuleDTO, WhitelistRuleExternalDTO
from core.dtos.chat.rules.nft import NftEligibilityRuleDTO, NftRuleEligibilitySummaryDTO
from core.dtos.base import NftItemAttributeDTO

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


class AddChatCPO(BaseFDO):
    chat_identifier: Annotated[str | int, AfterValidator(validate_chat_identifier)]


class EditChatCPO(BaseFDO):
    description: str | None


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


class NftItemAttributeFDO(BaseFDO, NftItemAttributeDTO):
    ...


class TelegramChatNFTCollectionRuleCPO(BaseTelegramChatRuleCPO):
    required_attributes: list[NftItemAttributeFDO] | None = None


class ChatEligibilityRuleFDO(BaseFDO, ChatEligibilityRuleDTO):
    @field_serializer("expected", return_type=float | int)
    def preprocess_expected(self, v: int) -> float | int:
        if not v or self.category != EligibilityCheckType.JETTON:
            return v

        return to_amount(v)


class NftEligibilityRuleFDO(BaseFDO, NftEligibilityRuleDTO):
    required_attributes: list[NftItemAttributeFDO] | None


class NftRuleEligibilitySummaryFDO(BaseFDO, NftRuleEligibilitySummaryDTO):
    required_attributes: list[NftItemAttributeFDO] | None


class TelegramChatWithRulesFDO(BaseFDO):
    chat: TelegramChatFDO
    rules: list[ChatEligibilityRuleFDO | NftEligibilityRuleFDO]

    @classmethod
    def from_dto(cls, dto: TelegramChatWithRulesDTO) -> Self:
        mapping = {
            EligibilityCheckType.NFT_COLLECTION: NftEligibilityRuleFDO,
        }
        return cls(
            chat=TelegramChatFDO.model_validate(dto.chat.model_dump()),
            rules=[
                mapping.get(rule.category, ChatEligibilityRuleFDO).model_validate(
                    rule.model_dump()
                )
                for rule in dto.rules
            ],
        )


class RuleEligibilitySummaryFDO(BaseFDO, RuleEligibilitySummaryDTO):
    @field_serializer("expected", return_type=float | int)
    def preprocess_expected(self, v: int) -> float | int:
        if not v or self.category != EligibilityCheckType.JETTON:
            return v

        return to_amount(v)


class TelegramChatWithEligibilitySummaryFDO(BaseFDO):
    """
    Chat with eligibility rules. Returns not only chat and rules data,
    but whether user is eligible for chat
    """

    chat: TelegramChatFDO
    rules: list[RuleEligibilitySummaryFDO | NftRuleEligibilitySummaryFDO]

    @classmethod
    def from_dto(cls, dto: TelegramChatWithEligibilitySummaryDTO) -> Self:
        mapping = {
            EligibilityCheckType.NFT_COLLECTION: NftRuleEligibilitySummaryFDO,
        }
        return cls(
            chat=TelegramChatFDO.model_validate(dto.chat.model_dump()),
            rules=[
                mapping.get(rule.category, RuleEligibilitySummaryFDO).model_validate(
                    rule.model_dump()
                )
                for rule in dto.rules
            ],
        )


class CreateWhitelistRuleBaseCPO(BaseFDO):
    name: Annotated[str, Field(min_length=1, max_length=255)]
    description: Annotated[str | None, Field(min_length=0, max_length=255)] = None


class CreateWhitelistRuleCPO(CreateWhitelistRuleBaseCPO):
    users: list[int]


class CreateWhitelistRuleExternalCPO(CreateWhitelistRuleBaseCPO):
    url: AnyHttpUrl


class UpdateWhitelistRuleCPO(CreateWhitelistRuleCPO):
    is_enabled: bool


class UpdateWhitelistRuleExternalCPO(CreateWhitelistRuleExternalCPO):
    is_enabled: bool


class WhitelistRuleFDO(BaseFDO, WhitelistRuleDTO):
    ...


class WhitelistRuleExternalFDO(BaseFDO, WhitelistRuleExternalDTO):
    ...
