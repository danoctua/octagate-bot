import logging
from abc import ABC, abstractmethod

from slugify import slugify
from sqlalchemy import func, desc
from sqlalchemy.exc import NoResultFound
from telethon.tl.types import Channel

from core.dtos.chat import (
    TelegramChatEligibilityRulesDTO,
    TelegramChatJettonRuleDTO,
    TelegramChatNFTCollectionRuleDTO,
    TelegramChatEligibilitySummaryDTO,
    TelegramChatEligibilityItemDTO,
    EligibilityCheckType,
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
            # TODO: handle cases with the same slug
            slug=slugify(entity.title),
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
        chat.slug = slugify(entity.title)
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

    def get_all(self, chat_ids: list[int] | None = None) -> list[TelegramChat]:
        query = self.db_session.query(TelegramChat)
        if chat_ids:
            query = query.filter(TelegramChat.id.in_(chat_ids))

        query = query.order_by(TelegramChat.id)
        return query.all()

    def refresh_invite_link(self, chat_id: int, invite_link: str) -> TelegramChat:
        chat = self.get(chat_id)
        chat.invite_link = invite_link
        self.db_session.commit()
        logger.debug(f"Telegram Chat {chat.title!r} invite link updated.")
        return chat

    def get_by_slug(self, slug: str) -> TelegramChat:
        return (
            self.db_session.query(TelegramChat).filter(TelegramChat.slug == slug).one()
        )


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

    def get_members_count(self, chat_id: int) -> int:
        return (
            self.db_session.query(TelegramChatUser)
            .filter(TelegramChatUser.chat_id == chat_id)
            .count()
        )

    def get_members_count_by_chat_id(
        self, chat_ids: list[int] | None = None
    ) -> dict[int, int]:
        query = self.db_session.query(
            TelegramChatUser.chat_id, func.count(TelegramChatUser.user_id)
        )
        if chat_ids:
            query = query.filter(TelegramChatUser.chat_id.in_(chat_ids))

        query = query.group_by(TelegramChatUser.chat_id)
        return dict(query.all())

    def get_all(self, user_ids: list[int] | None = None) -> list[TelegramChatUser]:
        query = self.db_session.query(TelegramChatUser)

        if user_ids:
            query = query.filter(TelegramChatUser.user_id.in_(user_ids))

        return query.all()

    def find(self, chat_id: int, user_id: int) -> TelegramChatUser | None:
        try:
            return self.get(chat_id, user_id)
        except NoResultFound:
            return None

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

    def get_eligibility_rules(
        self, chat_id: int, enabled_only: bool = True
    ) -> TelegramChatEligibilityRulesDTO:
        """
        Get eligibility rules for the chat based on the database records
        :param chat_id: Chat ID for which the rules are to be fetched
        :param enabled_only: Fetch only enabled rules. Set to False if you request rules for management purposes
        :return: Eligibility rules for the chat
        """
        telegram_chat_jetton_service = TelegramChatJettonService(self.db_session)
        all_jetton_rules = telegram_chat_jetton_service.get_all(
            chat_id, enabled_only=enabled_only
        )
        telegram_chat_nft_collection_service = TelegramChatNFTCollectionService(
            self.db_session
        )
        all_nft_collections = telegram_chat_nft_collection_service.get_all(
            chat_id, enabled_only=enabled_only
        )
        return TelegramChatEligibilityRulesDTO(
            jettons=all_jetton_rules,
            nft_collections=all_nft_collections,
        )

    @classmethod
    def is_user_eligible_chat_member(
        cls,
        eligibility_rules: TelegramChatEligibilityRulesDTO,
        user_jettons: list[JettonWallet],
        user_nft_items: list[NftItem],
        chat_member: TelegramChatUser | None = None,
    ) -> TelegramChatEligibilitySummaryDTO:
        """
        The rule is to have all required jetton balance OR all NFT items from the required collections

        :param eligibility_rules: Rules for eligibility to join the chat
        :param user_jettons: Jetton balances of the user
        :param user_nft_items: NFT items of the user
        :param chat_member: Chat member record
        :return: Summary of eligibility check
        """
        items = []
        user_jettons_by_master_address = {
            jetton_wallet.jetton_master_address: jetton_wallet
            for jetton_wallet in user_jettons
        }
        # Check if the user has all required jetton balances
        items.extend(
            [
                TelegramChatEligibilityItemDTO(
                    category=EligibilityCheckType.JETTON,
                    expected=rule.threshold,
                    title=rule.jetton.name,
                    address_raw=rule.address,
                    current=(
                        user_jetton_wallet.balance
                        if (
                            user_jetton_wallet := user_jettons_by_master_address.get(
                                rule.address
                            )
                        )
                        else 0
                    ),
                    is_enabled=rule.is_enabled,
                )
                for rule in eligibility_rules.jettons
            ]
        )
        # Check if the user has all required NFT items
        items.extend(
            [
                TelegramChatEligibilityItemDTO(
                    category=EligibilityCheckType.NFT_COLLECTION,
                    expected=rule.threshold,
                    title=rule.nft_collection.name,
                    address_raw=rule.address,
                    current=(
                        len(
                            [
                                nft_item.collection_address == rule.address
                                for nft_item in user_nft_items
                            ]
                        )
                    ),
                    is_enabled=rule.is_enabled,
                )
                for rule in eligibility_rules.nft_collections
            ]
        )
        return TelegramChatEligibilitySummaryDTO(
            items=items, is_admin=bool(chat_member and chat_member.is_admin)
        )

    def is_chat_member(self, chat_id: int, user_id: int) -> bool:
        return (
            self.db_session.query(TelegramChatUser)
            .filter(
                TelegramChatUser.chat_id == chat_id, TelegramChatUser.user_id == user_id
            )
            .count()
            > 0
        )

    def promote_whale_admin(self, chat_id: int, user_id: int) -> None:
        chat_user = self.get(chat_id, user_id)
        chat_user.is_whale_admin = True
        self.db_session.commit()
        logger.debug(f"Telegram Chat User {chat_user!r} promoted to whale admin.")

    def demote_whale_admin(self, chat_id: int, user_id: int) -> None:
        chat_user = self.get(chat_id, user_id)
        chat_user.is_whale_admin = False
        self.db_session.commit()
        logger.debug(f"Telegram Chat User {chat_user!r} demoted from whale admin.")

    def promote_admin(self, chat_id: int, user_id: int) -> None:
        chat_user = self.get(chat_id, user_id)
        chat_user.is_admin = True
        self.db_session.commit()
        logger.debug(f"Telegram Chat User {chat_user!r} promoted to admin.")

    def demote_admin(self, chat_id: int, user_id: int) -> None:
        chat_user = self.get(chat_id, user_id)
        chat_user.is_admin = False
        self.db_session.commit()
        logger.debug(f"Telegram Chat User {chat_user!r} demoted from admin.")

    def delete(self, chat_id: int, user_id: int) -> None:
        self.db_session.query(TelegramChatUser).filter(
            TelegramChatUser.chat_id == chat_id,
            TelegramChatUser.user_id == user_id,
        ).delete(synchronize_session="fetch")
        self.db_session.commit()
        logger.debug(f"Telegram Chat User {user_id!r} in chat {chat_id!r} deleted.")


TelegramChatRuleType = TelegramChatJetton | TelegramChatNFTCollection
TelegramChatRuleDTOType = TelegramChatJettonRuleDTO | TelegramChatNFTCollectionRuleDTO


class TelegramChatRuleBaseService(BaseService, ABC):
    model: type[TelegramChatRuleType]
    dto: type[TelegramChatJettonRuleDTO]

    def create(self, dto: TelegramChatRuleDTOType) -> TelegramChatRuleType:
        new_rule = self.model(**dto.model_dump())
        self.db_session.add(new_rule)
        self.db_session.commit()
        logger.debug(f"Telegram Chat Rule {new_rule!r} created.")
        return new_rule

    @abstractmethod
    def get(self, chat_id: int, address: str) -> TelegramChatRuleType:
        ...

    def update(self, chat: TelegramChatRuleDTOType) -> TelegramChatRuleType:
        rule = self.get(chat.chat_id, chat.address)
        rule.threshold = chat.threshold
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

    def toggle_rule(
        self, chat_id: int, address: str, is_enabled: bool
    ) -> TelegramChatRuleType:
        rule = self.get(chat_id, address)
        rule.is_enabled = is_enabled
        self.db_session.commit()
        logger.debug(f"Telegram Chat Rule {rule!r} toggled.")
        return rule

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
    dto = TelegramChatJettonRuleDTO

    def get(self, chat_id: int, jetton_address: str) -> TelegramChatJetton:
        return (
            self.db_session.query(TelegramChatJetton)
            .filter(
                TelegramChatJetton.chat_id == chat_id,
                TelegramChatJetton.address == jetton_address,
            )
            .one()
        )


class TelegramChatNFTCollectionService(TelegramChatRuleBaseService):
    model = TelegramChatNFTCollection
    dto = TelegramChatNFTCollectionRuleDTO

    def get(self, chat_id: int, collection_address: str) -> TelegramChatNFTCollection:
        return (
            self.db_session.query(TelegramChatNFTCollection)
            .filter(
                TelegramChatNFTCollection.chat_id == chat_id,
                TelegramChatNFTCollection.address == collection_address,
            )
            .one()
        )
