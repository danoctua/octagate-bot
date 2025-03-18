from pydantic import BaseModel, computed_field
from pytonapi.utils import raw_to_userfriendly

from core.dtos.base import NftItemAttributeDTO
from core.dtos.chat import TelegramChatDTO
from core.dtos.chat.rules import EligibilityCheckType, ChatEligibilityRuleDTO
from core.dtos.chat.rules.nft import NftRuleEligibilitySummaryDTO


class EligibilitySummaryInternalDTO(BaseModel):
    """
    Used for internal purposes to check if chat is eligible for promotion
    """

    id: int
    category: EligibilityCheckType
    title: str
    address_raw: str | None = None  # required for blockchain rules only
    actual: float | int = 0.0
    expected: float | int
    is_enabled: bool
    required_attributes: list[NftItemAttributeDTO] | None = None

    @property
    def address(self):
        if not self.address_raw:
            return None
        return raw_to_userfriendly(self.address_raw)

    @computed_field(return_type=bool)
    def is_eligible(self):
        return self.actual >= self.expected

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} "
            f"{self.category=} "
            f"{self.title=} "
            f"{self.address=} "
            f"{self.actual=} "
            f"{self.expected=}>"
        )


class RulesEligibilitySummaryInternalDTO(BaseModel):
    """
    Used for internal purposes to check if chat is eligible for promotion
    """

    items: list[EligibilitySummaryInternalDTO]
    is_admin: bool

    def __bool__(self):
        return any(item.is_eligible for item in self.items)

    def __repr__(self):
        return f"<{self.__class__.__name__} ({self.items=}) {self.is_admin=}>"


class RuleEligibilitySummaryDTO(ChatEligibilityRuleDTO):
    actual: float | None = None
    is_eligible: bool = False


class TelegramChatWithEligibilitySummaryDTO(BaseModel):
    chat: TelegramChatDTO
    rules: list[RuleEligibilitySummaryDTO | NftRuleEligibilitySummaryDTO]
