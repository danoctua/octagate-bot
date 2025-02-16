import logging
from collections import defaultdict

from sqlalchemy.orm import Session

from core.actions.base import BaseAction
from core.constants import CUSTOM_TITLE_TEMPLATE
from core.dtos.chat import (
    TelegramChatEligibilitySummaryDTO,
    TelegramChatEligibilityRulesDTO,
)
from core.models.chat import TelegramChatJetton, TelegramChatUser
from core.models.wallet import JettonWallet
from core.services.chat import TelegramChatUserService, TelegramChatJettonService
from core.services.nft import NftItemService
from core.services.supertelethon import TelethonService
from core.services.wallet import JettonWalletService

logger = logging.getLogger(__name__)


class AuthorizationAction(BaseAction):
    def __init__(self, db_session: Session) -> None:
        super().__init__(db_session)
        self.jetton_wallet_service = JettonWalletService(db_session)
        self.telegram_chat_user_service = TelegramChatUserService(db_session)
        self.telegram_chat_jetton_service = TelegramChatJettonService(db_session)

    def is_user_eligible_chat_member(
        self, user_id: int, chat_id: int
    ) -> TelegramChatEligibilitySummaryDTO:
        """
        Check if user is eligible to be a chat member
        :param user_id:
        :param chat_id:
        :return:
        """
        user = self.user_service.get(user_id=user_id)
        telegram_chat_user = self.telegram_chat_user_service.find(
            chat_id=chat_id, user_id=user.id
        )
        eligibility_rules = self.telegram_chat_user_service.get_eligibility_rules(
            chat_id=chat_id
        )
        nft_item_service = NftItemService(self.db_session)
        user_nft_items = nft_item_service.get_all(owner_address=user.wallet.address)
        user_jettons = self.jetton_wallet_service.get_all(
            owner_address=user.wallet.address
        )

        eligibility_summary = (
            self.telegram_chat_user_service.is_user_eligible_chat_member(
                eligibility_rules=eligibility_rules,
                user_jettons=user_jettons,
                user_nft_items=user_nft_items,
                chat_member=telegram_chat_user,
            )
        )
        return eligibility_summary

    def get_ineligible_chat_members(
        self,
        chat_members: list[TelegramChatUser],
    ) -> list[TelegramChatUser]:
        """
        Process list of the current chat members and return the ones that are not eligible to be in the chat
        :param chat_members: list of chat members
        :return: list of ineligible chat members
        """
        members_per_chat = defaultdict(list)
        eligibility_rules_per_chat: dict[int, TelegramChatEligibilityRulesDTO] = {}
        for chat_member in chat_members:
            members_per_chat[chat_member.chat_id].append(chat_member)
            eligibility_rules_per_chat[
                chat_member.chat_id
            ] = self.telegram_chat_user_service.get_eligibility_rules(
                chat_id=chat_member.chat_id
            )

        nft_item_service = NftItemService(self.db_session)
        jetton_wallet_service = JettonWalletService(self.db_session)

        unique_users = {chat_member.user for chat_member in chat_members}

        nft_items_per_user = defaultdict(list)
        jetton_wallets_per_user = defaultdict(list)

        for user in unique_users:
            if not user.wallet:
                continue

            nft_items_per_user[user] = nft_item_service.get_all(
                owner_address=user.wallet.address
            )
            jetton_wallets_per_user[user] = jetton_wallet_service.get_all(
                owner_address=user.wallet.address
            )

        ineligible_members = []
        for chat, members in members_per_chat.items():
            for member in members:
                if not (
                    eligibility_summary
                    := self.telegram_chat_user_service.is_user_eligible_chat_member(
                        eligibility_rules=eligibility_rules_per_chat[chat],
                        user_jettons=jetton_wallets_per_user.get(member.user, []),
                        user_nft_items=nft_items_per_user.get(member.user, []),
                        chat_member=member,
                    )
                ):
                    logger.debug(
                        f"User {member.user.telegram_id!r} is not eligible to be in chat {chat!r}."
                        f"Eligibility summary: {eligibility_summary!r}"
                    )
                    ineligible_members.append(member)

        return ineligible_members

    async def kick_ineligible_chat_members(
        self,
        chat_members: list[TelegramChatUser],
    ) -> None:
        ineligible_members = self.get_ineligible_chat_members(chat_members=chat_members)
        if not ineligible_members:
            logger.info("No ineligible chat members found")
            return

        telethon_service = TelethonService()
        await telethon_service.start()
        for member in ineligible_members:
            await telethon_service.kick_chat_member(
                chat_id=member.chat_id, telegram_user_id=member.user.telegram_id
            )
            self.telegram_chat_user_service.delete(
                chat_id=member.chat_id, user_id=member.user.id
            )
            logger.info(
                f"User {member.user.telegram_id!r} was kicked from chat {member.chat_id!r}"
            )
        else:
            logger.info("No ineligible chat members found")
        await telethon_service.stop()

    @staticmethod
    def get_whale_title(
        chat_jetton_rule: TelegramChatJetton, user_jetton_wallet: JettonWallet
    ) -> str:
        whale_template = chat_jetton_rule.whale_label_template or CUSTOM_TITLE_TEMPLATE
        custom_title = whale_template.format(rank=user_jetton_wallet.rating or "XX")
        return custom_title

    def get_chat_user_by_telegram_id(
        self, chat_id: int, telegram_id: int
    ) -> TelegramChatUser | None:
        user = self.user_service.get_by_telegram_id(telegram_id=telegram_id)
        if not user.wallet:
            logger.warning(
                f"User {user.telegram_id!r} has no wallet connected and can't be operated"
            )
            return

        return self.telegram_chat_user_service.find(chat_id=chat_id, user_id=user.id)

    async def promote_whale_admin(
        self, chat_id: int, user_id: int, jetton_address: str
    ) -> None:
        chat_member = self.get_chat_user_by_telegram_id(
            chat_id=chat_id, telegram_id=user_id
        )
        if not chat_member:
            logger.warning(
                f"User {chat_member.user.telegram_id!r} is not a chat member and can't be promoted"
            )
            return

        chat_jetton_rule = self.telegram_chat_jetton_service.get(
            chat_id=chat_id,
            jetton_address=jetton_address,
        )
        user_jetton_wallet = self.jetton_wallet_service.get_by_owner_address(
            owner_address=chat_member.user.wallet.address,
            jetton_master_address=jetton_address,
        )

        if not self.telegram_chat_jetton_service.is_chat_whale(
            chat_jetton_rule=chat_jetton_rule, user_jetton_wallet=user_jetton_wallet
        ):
            logger.warning(
                f"User {chat_member.user.telegram_id!r} is not a whale and can't be promoted"
            )
            return

        if chat_member.is_admin:
            logger.info(
                f"User {chat_member.user.telegram_id!r} is a non-whale admin. Skipping"
            )
            return

        if not chat_member.is_whale_admin:
            logger.info(
                f"User {chat_member.user.telegram_id!r} is not a whale admin. Promoting"
            )
            telethon_service = TelethonService()
            await telethon_service.start()
            await telethon_service.promote_user(
                chat_id=chat_id,
                telegram_user_id=chat_member.user.telegram_id,
                custom_title=self.get_whale_title(
                    chat_jetton_rule=chat_jetton_rule,
                    user_jetton_wallet=user_jetton_wallet,
                ),
            )
            self.telegram_chat_user_service.promote_whale_admin(
                chat_id=chat_id, user_id=chat_member.user.id
            )

    async def demote_whale_admin(self, chat_id: int, telegram_id: int) -> None:
        chat_member = self.get_chat_user_by_telegram_id(
            chat_id=chat_id, telegram_id=telegram_id
        )
        if not chat_member:
            logger.warning(
                f"User {chat_member.user.telegram_id!r} is not a chat member and can't be demoted"
            )
            return

        if not chat_member.is_whale_admin:
            logger.info(
                f"User {chat_member.user.telegram_id!r} is not a whale admin. Skipping"
            )
            return

        if chat_member.is_admin:
            logger.info(
                f"User {chat_member.user.telegram_id!r} is a non-whale admin. Skipping"
            )
            return

        logger.info(f"User {chat_member.user.telegram_id!r} is a whale admin. Demoting")
        telethon_service = TelethonService()
        await telethon_service.start()
        await telethon_service.demote_user(
            chat_id=chat_id,
            telegram_user_id=chat_member.user.telegram_id,
        )
        self.telegram_chat_user_service.demote_whale_admin(
            chat_id=chat_id, user_id=chat_member.user.id
        )
