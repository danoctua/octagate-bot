import logging

from sqlalchemy.orm import Session

from core.constants import CUSTOM_TITLE_TEMPLATE
from core.dtos.chat import TelegramChatEligibilitySummaryDTO
from core.models.chat import TelegramChatJetton, TelegramChatUser
from core.models.wallet import JettonWallet
from core.services.chat import TelegramChatUserService, TelegramChatJettonService
from core.services.nft import NftItemService
from core.services.supertelethon import TelethonService
from core.services.user import UserService
from core.services.wallet import JettonWalletService

logger = logging.getLogger(__name__)


class AuthorizationAction:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session
        self.user_service = UserService(db_session)
        self.jetton_wallet_service = JettonWalletService(db_session)
        self.telegram_chat_user_service = TelegramChatUserService(db_session)
        self.telegram_chat_jetton_service = TelegramChatJettonService(db_session)
        self.telethon_service = TelethonService()

    def is_user_eligible_chat_member(
        self, user_id: int, chat_id: int
    ) -> TelegramChatEligibilitySummaryDTO:
        user = self.user_service.get(user_id=user_id)
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
            )
        )
        return eligibility_summary

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

    def promote_whale_admin(
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
            self.telethon_service.promote_user(
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

    def demote_whale_admin(self, chat_id: int, telegram_id: int) -> None:
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
        self.telethon_service.demote_user(
            chat_id=chat_id,
            telegram_user_id=chat_member.user.telegram_id,
        )
        self.telegram_chat_user_service.demote_whale_admin(
            chat_id=chat_id, user_id=chat_member.user.id
        )
