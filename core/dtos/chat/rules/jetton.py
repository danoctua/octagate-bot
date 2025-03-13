from pydantic import BaseModel


class BaseTelegramChatJettonRuleDTO(BaseModel):
    address: str
    threshold: int
    is_enabled: bool


class CreateTelegramChatJettonRuleDTO(BaseTelegramChatJettonRuleDTO):
    chat_id: int


class UpdateTelegramChatJettonRuleDTO(BaseTelegramChatJettonRuleDTO):
    ...
