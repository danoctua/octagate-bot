import dataclasses
import enum

from pydantic import BaseModel, field_serializer
from pytonapi.utils import raw_to_userfriendly, to_nano

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
    jetton_address: str
    threshold: int
    whale_threshold: int | None = None
    whale_label_template: str | None = None

    @field_serializer("threshold", "whale_threshold")
    def serialize_threshold(self, val: float | None) -> float:
        if not val:
            return val

        return to_nano(val)


class TelegramChatNFTCollectionRuleDTO(BaseModel):
    chat_id: int
    collection_address: str
