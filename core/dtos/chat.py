from pydantic import BaseModel


from core.models.chat import TelegramChatJetton, TelegramChatNFTCollection


class TelegramChatEligibilityRules(BaseModel):
    jettons: list[TelegramChatJetton]
    nft_collections: list[TelegramChatNFTCollection]


class TelegramChatJettonRule(BaseModel):
    chat_id: int
    address: str
    threshold: int
    whale_threshold: int
    whale_custom_label: str


class TelegramChatNFTCollectionRule(BaseModel):
    chat_id: int
    address: str
