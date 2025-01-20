import logging
from abc import ABC, abstractmethod

from sqlalchemy.exc import NoResultFound
from telethon.tl.types import Channel

from core.dtos.chat import (
    TelegramChatEligibilityRules,
    TelegramChatJettonRule,
    TelegramChatNFTCollectionRule,
)
from core.models.blockchain import NftItem
from core.models.wallet import JettonWallet
from core.models.chat import (
    TelegramChat,
    TelegramChatUser,
    TelegramChatJetton,
    TelegramChatNFTCollection,
)
from core.services.base import BaseService


logger = logging.getLogger(__name__)


class TelegramChatService(BaseService):
    def create(self, chat_id: int, entity: Channel, logo_path: str) -> TelegramChat:
        chat = TelegramChat(
            id=chat_id,
            username=entity.username,
            title=entity.title,
            is_forum=entity.forum,
            logo_path=logo_path,
        )
        self.db_session.add(chat)
        self.db_session.commit()
        logger.debug(f"Telegram Chat {chat.title!r} created.")
        return chat

    def update(
        self, entity: Channel, chat: TelegramChat, logo_path: str
    ) -> TelegramChat:
        chat.username = entity.username
        chat.title = entity.title
        chat.is_forum = entity.forum
        chat.logo_path = logo_path
        self.db_session.commit()
        logger.debug(f"Telegram Chat {chat.title!r} updated.")
        return chat

    def create_or_update(
        self, chat_id: int, entity: Channel, logo_path: str
    ) -> TelegramChat:
        try:
            chat = self.get(chat_id=chat_id)
            return self.update(entity, chat, logo_path=logo_path)
        except NoResultFound:
            logger.debug(
                f"No Telegram Chat for ID {entity.id!r} found. Creating new Telegram Chat."
            )
            return self.create(chat_id=chat_id, entity=entity, logo_path=logo_path)

    def get(self, chat_id: int) -> TelegramChat:
        return (
            self.db_session.query(TelegramChat).filter(TelegramChat.id == chat_id).one()
        )

    def refresh_invite_link(self, chat_id: int, invite_link: str) -> TelegramChat:
        chat = self.get(chat_id)
        chat.invite_link = invite_link
        self.db_session.commit()
        logger.debug(f"Telegram Chat {chat.title!r} invite link updated.")
        return chat


class TelegramChatUserService(BaseService):
    def create(
        self, chat_id: int, user_id: int, is_admin: bool, is_whale_admin: bool
    ) -> TelegramChatUser:
        chat_user = TelegramChatUser(
            chat_id=chat_id,
            user_id=user_id,
            is_admin=is_admin,
            is_whale_admin=is_whale_admin,
        )
        self.db_session.add(chat_user)
        self.db_session.commit()
        logger.debug(f"Telegram Chat User {chat_user!r} created.")
        return chat_user

    def get(self, chat_id: int, user_id: int) -> TelegramChatUser:
        return (
            self.db_session.query(TelegramChatUser)
            .filter(
                TelegramChatUser.chat_id == chat_id, TelegramChatUser.user_id == user_id
            )
            .one()
        )

    def update(
        self, chat_user: TelegramChatUser, is_admin: bool, is_whale_admin: bool
    ) -> TelegramChatUser:
        chat_user.is_admin = is_admin
        chat_user.is_whale_admin = is_whale_admin
        self.db_session.commit()
        logger.debug(f"Telegram Chat User {chat_user!r} updated.")
        return chat_user

    def create_or_update(
        self, chat_id: int, user_id: int, is_admin: bool, is_whale_admin: bool
    ) -> TelegramChatUser:
        try:
            chat_user = self.get(chat_id, user_id)
            return self.update(
                chat_user=chat_user, is_admin=is_admin, is_whale_admin=is_whale_admin
            )
        except NoResultFound:
            logger.debug(
                f"No Telegram Chat User for chat_id {chat_id!r} and user_id {user_id!r} found. Creating new Telegram Chat User."
            )
            return self.create(chat_id, user_id, is_admin, is_whale_admin)

    def get_eligibility_rules(self, chat_id: int) -> TelegramChatEligibilityRules:
        """
        Get eligibility rules for the chat based on the database records
        :param chat_id:
        :return:
        """
        telegram_chat_jetton_service = TelegramChatJettonService(self.db_session)
        all_jetton_rules = telegram_chat_jetton_service.get_all(chat_id)
        telegram_chat_nft_collection_service = TelegramChatNFTCollectionService(
            self.db_session
        )
        all_nft_collections = telegram_chat_nft_collection_service.get_all(chat_id)
        return TelegramChatEligibilityRules(
            jettons=all_jetton_rules,
            nft_collections=all_nft_collections,
        )

    @classmethod
    def is_user_eligible_chat_member(
        cls,
        eligibility_rules: TelegramChatEligibilityRules,
        user_jettons: list[JettonWallet],
        user_nft_items: list[NftItem],
    ) -> bool:
        """
        The rule is to have all required jetton balance OR all NFT items from the required collections

        :param eligibility_rules: Rules for eligibility to join the chat
        :param user_jettons: Jetton balances of the user
        :param user_nft_items: NFT items of the user
        :return: True if the user is eligible to join the chat, False otherwise
        """
        has_all_jettons_required = True
        user_jettons_by_master_address = {
            jetton_wallet.jetton_master_address: jetton_wallet
            for jetton_wallet in user_jettons
        }
        for rule in eligibility_rules.jettons:
            if not (
                user_jetton_wallet := user_jettons_by_master_address.get(
                    rule.jetton_address
                )
            ):
                has_all_jettons_required = False
                break

            if not user_jetton_wallet.balance >= rule.threshold:
                has_all_jettons_required = False
                break

        if has_all_jettons_required:
            return True

        user_nft_items_by_collection_address = {
            nft_item.collection_address: nft_item for nft_item in user_nft_items
        }
        return all(
            nft_item.collection_address in user_nft_items_by_collection_address
            for nft_item in eligibility_rules.nft_collections
        )


TelegramChatRuleType = TelegramChatJetton | TelegramChatNFTCollection
TelegramChatRuleDTOType = TelegramChatJettonRule | TelegramChatNFTCollectionRule


class TelegramChatRuleBaseService(BaseService, ABC):
    model: type[TelegramChatRuleType]
    dto: type[TelegramChatJettonRule]

    def create(self, dto: TelegramChatRuleDTOType) -> TelegramChatRuleType:
        new_rule = self.model(**dto.model_dump())
        self.db_session.add(new_rule)
        self.db_session.commit()
        logger.debug(f"Telegram Chat Rule {new_rule!r} created.")
        return new_rule

    @abstractmethod
    def get(self, chat_id: int, address: str) -> TelegramChatRuleType:
        ...

    def get_all(
        self, chat_id: int | None = None, enabled_only: bool = False
    ) -> list[TelegramChatRuleType]:
        query = self.db_session.query(self.model)
        if chat_id is not None:
            query = query.filter(self.model.chat_id == chat_id)

        if enabled_only:
            query = query.filter(self.model.is_enabled.is_(True))

        return query.all()

    def enable_rule(self, chat_id: int, address: str) -> None:
        rule = self.get(chat_id, address)
        rule.is_enabled = True
        self.db_session.commit()
        logger.debug(f"Telegram Chat Rule {rule!r} enabled.")

    def disable_rule(self, chat_id: int, address: str) -> None:
        rule = self.get(chat_id, address)
        rule.is_enabled = False
        self.db_session.commit()
        logger.debug(f"Telegram Chat Rule {rule!r} disabled.")


class TelegramChatJettonService(TelegramChatRuleBaseService):
    model = TelegramChatJetton
    dto = TelegramChatJettonRule

    def update(
        self,
        chat_id: int,
        address: str,
        threshold: int,
        whale_threshold: int | None = None,
        whale_label_template: str | None = None,
    ) -> None:
        telegram_chat_jetton = self.get(chat_id, address)
        telegram_chat_jetton.threshold = threshold
        telegram_chat_jetton.whale_threshold = whale_threshold
        telegram_chat_jetton.whale_label_template = whale_label_template
        self.db_session.commit()
        logger.debug(f"Telegram Chat Jetton {telegram_chat_jetton!r} updated.")

    def get(self, chat_id: int, jetton_address: str) -> type[TelegramChatJetton]:
        return (
            self.db_session.query(TelegramChatJetton)
            .filter(
                TelegramChatJetton.chat_id == chat_id,
                TelegramChatJetton.jetton_address == jetton_address,
            )
            .one()
        )


class TelegramChatNFTCollectionService(TelegramChatRuleBaseService):
    model = TelegramChatNFTCollection
    dto = TelegramChatNFTCollectionRule

    def get(self, chat_id: int, collection_address: str) -> TelegramChatNFTCollection:
        return (
            self.db_session.query(TelegramChatNFTCollection)
            .filter(
                TelegramChatNFTCollection.chat_id == chat_id,
                TelegramChatNFTCollection.collection_address == collection_address,
            )
            .one()
        )
