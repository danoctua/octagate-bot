import logging
from collections import defaultdict

from sqlalchemy.orm import Session

from core.actions.base import BaseAction
from core.dtos.chat.rules import (
    EligibilityCheckType,
    TelegramChatEligibilityRulesDTO,
)
from core.dtos.chat.rules.summary import (
    EligibilitySummaryInternalDTO,
    RulesEligibilitySummaryInternalDTO,
)
from core.models.user import User
from core.models.wallet import JettonWallet
from core.models.blockchain import NftItem
from core.models.chat import (
    TelegramChatUser,
    TelegramChatWhitelistExternalSource,
    TelegramChatWhitelist,
)
from core.services.chat.rule.whitelist import (
    TelegramChatExternalSourceService,
    TelegramChatWhitelistService,
)
from core.services.chat.rule.blockchain import (
    TelegramChatJettonService,
    TelegramChatNFTCollectionService,
)
from core.services.chat.user import TelegramChatUserService
from core.services.nft import NftItemService
from core.services.supertelethon import TelethonService
from core.services.wallet import JettonWalletService
from core.utils.nft import find_relevant_nft_items

logger = logging.getLogger(__name__)


class AuthorizationAction(BaseAction):
    """
    Actions related to user authorization in the chat

    This is the only low-level action that could be used in the high-level actions
    """

    def __init__(self, db_session: Session) -> None:
        super().__init__(db_session)
        self.jetton_wallet_service = JettonWalletService(db_session)
        self.telegram_chat_user_service = TelegramChatUserService(db_session)
        self.telegram_chat_jetton_service = TelegramChatJettonService(db_session)
        self.telegram_chat_nft_collection_service = TelegramChatNFTCollectionService(
            db_session
        )
        self.telegram_chat_external_source_service = TelegramChatExternalSourceService(
            db_session
        )
        self.telegram_chat_whitelist_group_service = TelegramChatWhitelistService(
            db_session
        )

    def is_user_eligible_chat_member(
        self, user_id: int, chat_id: int
    ) -> RulesEligibilitySummaryInternalDTO:
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
        eligibility_rules = self.get_eligibility_rules(chat_id=chat_id)
        nft_item_service = NftItemService(self.db_session)
        if user.wallet:
            user_nft_items = nft_item_service.get_all(owner_address=user.wallet.address)
            user_jettons = self.jetton_wallet_service.get_all(
                owner_address=user.wallet.address
            )
        else:
            user_nft_items = []
            user_jettons = []

        eligibility_summary = self.check_chat_member_eligibility(
            eligibility_rules=eligibility_rules,
            user=user,
            user_jettons=user_jettons,
            user_nft_items=user_nft_items,
            chat_member=telegram_chat_user,
        )
        return eligibility_summary

    def get_eligibility_rules(
        self, chat_id: int, enabled_only: bool = True
    ) -> TelegramChatEligibilityRulesDTO:
        """
        Get eligibility rules for the chat based on the database records
        :param chat_id: Chat ID for which the rules are to be fetched
        :param enabled_only: Fetch only enabled rules. Set to False if you request rules for management purposes
        :return: Eligibility rules for the chat
        """
        all_jetton_rules = self.telegram_chat_jetton_service.get_all(
            chat_id, enabled_only=enabled_only
        )
        all_nft_collections = self.telegram_chat_nft_collection_service.get_all(
            chat_id, enabled_only=enabled_only
        )
        all_external_source_rules = self.telegram_chat_external_source_service.get_all(
            chat_id, enabled_only=enabled_only
        )
        all_whitelist_groups = self.telegram_chat_whitelist_group_service.get_all(
            chat_id, enabled_only=enabled_only
        )
        return TelegramChatEligibilityRulesDTO(
            jettons=all_jetton_rules,
            nft_collections=all_nft_collections,
            whitelist_external_sources=all_external_source_rules,
            whitelist_sources=all_whitelist_groups,
        )

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
            ] = self.get_eligibility_rules(chat_id=chat_member.chat_id)

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
                    eligibility_summary := self.check_chat_member_eligibility(
                        eligibility_rules=eligibility_rules_per_chat[chat],
                        user=member.user,
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

    @classmethod
    def check_chat_member_eligibility(
        cls,
        eligibility_rules: TelegramChatEligibilityRulesDTO,
        user: User,
        user_jettons: list[JettonWallet],
        user_nft_items: list[NftItem],
        chat_member: TelegramChatUser | None = None,
    ) -> RulesEligibilitySummaryInternalDTO:
        """
        The rule is to have all required jetton balance OR all NFT items from the required collections

        :param eligibility_rules: Rules for eligibility to join the chat
        :param user: User to check
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
                EligibilitySummaryInternalDTO(
                    id=jetton.id,
                    category=EligibilityCheckType.JETTON,
                    expected=jetton.threshold,
                    title=jetton.jetton.name,
                    address_raw=jetton.address,
                    current=(
                        user_jetton_wallet.balance
                        if (
                            user_jetton_wallet := user_jettons_by_master_address.get(
                                jetton.address
                            )
                        )
                        else 0
                    ),
                    is_enabled=jetton.is_enabled,
                )
                for jetton in eligibility_rules.jettons
            ]
        )
        # Check if the user has all required NFT items
        items.extend(
            [
                EligibilitySummaryInternalDTO(
                    id=nft_collection.id,
                    category=EligibilityCheckType.NFT_COLLECTION,
                    expected=nft_collection.threshold,
                    title=nft_collection.nft_collection.name,
                    address_raw=nft_collection.address,
                    current=(
                        len(
                            find_relevant_nft_items(
                                rule=nft_collection, nft_items=user_nft_items
                            )
                        )
                    ),
                    is_enabled=nft_collection.is_enabled,
                    required_attributes=nft_collection.required_attributes,
                )
                for nft_collection in eligibility_rules.nft_collections
            ]
        )
        items.extend(
            [
                EligibilitySummaryInternalDTO(
                    id=external_source.id,
                    category=EligibilityCheckType.EXTERNAL_SOURCE,
                    expected=1,
                    title=external_source.name,
                    current=cls.is_whitelisted(user=user, rule=external_source),
                    is_enabled=external_source.is_enabled,
                )
                for external_source in eligibility_rules.whitelist_external_sources
            ]
        )
        items.extend(
            [
                EligibilitySummaryInternalDTO(
                    id=whitelist_group.id,
                    category=EligibilityCheckType.WHITELIST,
                    expected=1,
                    title=whitelist_group.name,
                    current=cls.is_whitelisted(user=user, rule=whitelist_group),
                    is_enabled=whitelist_group.is_enabled,
                )
                for whitelist_group in eligibility_rules.whitelist_sources
            ]
        )
        return RulesEligibilitySummaryInternalDTO(
            items=items, is_admin=bool(chat_member and chat_member.is_admin)
        )

    @staticmethod
    def is_whitelisted(
        user: User, rule: TelegramChatWhitelist | TelegramChatWhitelistExternalSource
    ) -> bool:
        """
        Check if user is in whitelist by the rule
        :param user: User to check
        :param rule: Whitelist rule to check
        :return: True if user is whitelisted
        """
        return user.telegram_id in rule.content

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
