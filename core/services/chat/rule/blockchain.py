import logging
from abc import ABC

from sqlalchemy import desc

from core.dtos.chat.rules.nft import (
    CreateTelegramChatNFTCollectionRuleDTO,
    UpdateTelegramChatNFTCollectionRuleDTO,
)
from core.dtos.chat.rules.jetton import (
    CreateTelegramChatJettonRuleDTO,
    UpdateTelegramChatJettonRuleDTO,
)
from core.models.chat import TelegramChatJetton, TelegramChatNFTCollection
from core.services.base import BaseService


logger = logging.getLogger(__name__)


TelegramChatRuleType = TelegramChatJetton | TelegramChatNFTCollection
CreateTelegramChatRuleDTOType = (
    CreateTelegramChatJettonRuleDTO | CreateTelegramChatNFTCollectionRuleDTO
)
UpdateTelegramChatRuleDTOType = (
    UpdateTelegramChatJettonRuleDTO | UpdateTelegramChatNFTCollectionRuleDTO
)


class TelegramChatBlockchainRuleBaseService(BaseService, ABC):
    model: type[TelegramChatRuleType]

    def create(self, dto: CreateTelegramChatRuleDTOType) -> TelegramChatRuleType:
        new_rule = self.model(**dto.model_dump())
        self.db_session.add(new_rule)
        self.db_session.commit()
        logger.debug(f"Telegram Chat Rule {new_rule!r} created.")
        return new_rule

    def get(self, id_: int) -> TelegramChatRuleType:
        return self.db_session.query(self.model).filter(self.model.id == id_).one()

    def update(
        self,
        rule_id: int,
        dto: UpdateTelegramChatRuleDTOType,
    ) -> TelegramChatRuleType:
        rule = self.get(rule_id)
        for key, value in dto.model_dump().items():
            setattr(rule, key, value)
        self.db_session.commit()
        logger.debug(f"{rule!r} updated.")
        return rule

    def get_all(
        self, chat_id: int | None = None, enabled_only: bool = True
    ) -> list[TelegramChatRuleType]:
        query = self.db_session.query(self.model)
        if chat_id is not None:
            query = query.filter(self.model.chat_id == chat_id)

        if enabled_only:
            query = query.filter(self.model.is_enabled.is_(True))

        query = query.order_by(desc(self.model.is_enabled), self.model.created_at)
        return query.all()


class TelegramChatJettonService(TelegramChatBlockchainRuleBaseService):
    model = TelegramChatJetton


class TelegramChatNFTCollectionService(TelegramChatBlockchainRuleBaseService):
    model = TelegramChatNFTCollection
