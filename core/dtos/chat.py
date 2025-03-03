import dataclasses
import enum

from pydantic import BaseModel
from pytonapi.utils import raw_to_userfriendly

from core.models.chat import TelegramChatJetton, TelegramChatNFTCollection
from core.utils.number import human_friendly_number


class EligibilityCheckType(enum.Enum):
    JETTON = "jetton"
    NFT_COLLECTION = "nft_collection"


@dataclasses.dataclass
class TelegramChatEligibilityRulesDTO:
    jettons: list[TelegramChatJetton]
    nft_collections: list[TelegramChatNFTCollection]


class TelegramChatEligibilityItemDTO(BaseModel):
    category: EligibilityCheckType
    title: str
    address_raw: str
    current: float | int = 0.0
    expected: float | int
    is_enabled: bool

    @property
    def address(self):
        return raw_to_userfriendly(self.address_raw)

    @property
    def is_eligible(self):
        return self.current >= self.expected

    @property
    def current_human_friendly(self) -> str:
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


class TelegramChatJettonRuleDTO(BaseModel):
    chat_id: int
    jetton_address: str
    threshold: int
    whale_threshold: int | None = None
    whale_label_template: str | None = None


class TelegramChatNFTCollectionRuleDTO(BaseModel):
    chat_id: int
    collection_address: str
