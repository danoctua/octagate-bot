import dataclasses
import enum

from pydantic import BaseModel
from pytonapi.utils import raw_to_userfriendly

from core.models.chat import TelegramChatJetton, TelegramChatNFTCollection


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
    current: float = 0.0
    expected: float

    @property
    def address(self):
        return raw_to_userfriendly(self.address_raw)

    @property
    def is_eligible(self):
        return self.current >= self.expected


class TelegramChatEligibilitySummaryDTO(BaseModel):
    items: list[TelegramChatEligibilityItemDTO]

    def __bool__(self):
        return any(item.is_eligible for item in self.items)


class TelegramChatJettonRuleDTO(BaseModel):
    chat_id: int
    address: str
    threshold: int
    whale_threshold: int
    whale_custom_label: str


class TelegramChatNFTCollectionRuleDTO(BaseModel):
    chat_id: int
    address: str
