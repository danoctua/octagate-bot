from pydantic import BaseModel

from core.dtos.chat import EligibilityCheckType
from core.utils.number import human_friendly_number


PROMOTE_NFT_COLLECTION_TEMPLATE = "https://getgems.io/collection/{collection_address}"
PROMOTE_JETTON_TEMPLATE = (
    "https://app.ston.fi/swap?chartVisible=false&ft=TON&tt={jetton_master_address}"
)


class TelegramChatFDO(BaseModel):
    id: int
    username: str | None
    title: str
    slug: str
    is_forum: bool
    logo_path: str | None


class TelegramChatEligibilityRuleFDO(BaseModel):
    category: EligibilityCheckType
    title: str
    promote_url: str
    expected: float
    photo_url: str | None = None

    @property
    def expected_human_friendly(self) -> str:
        return human_friendly_number(self.expected)


class TelegramChatWithRulesFDO(BaseModel):
    chat: TelegramChatFDO
    rules: list[TelegramChatEligibilityRuleFDO]
