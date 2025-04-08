from pydantic import BaseModel


class BaseTelegramChatToncoinRuleDTO(BaseModel):
    threshold: int
    is_enabled: bool


class CreateTelegramChatToncoinRuleDTO(BaseTelegramChatToncoinRuleDTO):
    chat_id: int


class UpdateTelegramChatToncoinRuleDTO(BaseTelegramChatToncoinRuleDTO):
    ...
