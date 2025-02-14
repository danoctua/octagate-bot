from pydantic import BaseModel, ConfigDict, computed_field, Field
from pydantic.alias_generators import to_camel

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
    join_url: str | None = None
    is_member: bool = False

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class TelegramChatEligibilityRuleFDO(BaseModel):
    category: EligibilityCheckType
    title: str
    expected: float
    actual: float | None = None
    photo_url: str | None = None
    is_eligible: bool = False
    blockchain_address: str | None = Field(None, exclude=True)

    @property
    def expected_human_friendly(self) -> str:
        return human_friendly_number(self.expected)

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

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class TelegramChatWithRulesFDO(BaseModel):
    chat: TelegramChatFDO
    rules: list[TelegramChatEligibilityRuleFDO]
