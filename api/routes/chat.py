import logging

from fastapi import APIRouter, Depends
from sqlalchemy.exc import NoResultFound

from api.deps import validate_access_token
from api.pos.chat import (
    TelegramChatWithRulesFDO,
    TelegramChatFDO,
    TelegramChatEligibilityRuleFDO,
)
from core.dtos.chat import TelegramChatEligibilitySummaryDTO
from core.services.chat import TelegramChatService, TelegramChatUserService
from core.services.db import DBService
from core.services.nft import NftItemService
from core.services.user import UserService
from core.services.wallet import JettonWalletService

logger = logging.getLogger(__name__)

chat_router = APIRouter(prefix="/chats")


@chat_router.get("/{slug}")
async def get_chat(
    slug: str,
    user_id: int = Depends(validate_access_token),
) -> TelegramChatWithRulesFDO:
    with DBService().db_session() as db_session:
        chat_service = TelegramChatService(db_session)
        try:
            chat = chat_service.get_by_slug(slug)
        except NoResultFound:
            logger.debug(f"Chat with slug {slug!r} not found")

        telegram_chat_user_service = TelegramChatUserService(db_session)
        eligibility_rules = telegram_chat_user_service.get_eligibility_rules(
            chat_id=chat.id
        )

        user_service = UserService(db_session)
        user = user_service.get(user_id)

        if user.wallet:
            nft_item_service = NftItemService(db_session)
            user_nft_items = nft_item_service.get_all(owner_address=user.wallet.address)
            jetton_wallet_service = JettonWalletService(db_session)
            user_jettons = jetton_wallet_service.get_all(
                owner_address=user.wallet.address
            )
        else:
            user_nft_items = []
            user_jettons = []

        eligibility_summary: TelegramChatEligibilitySummaryDTO = (
            telegram_chat_user_service.is_user_eligible_chat_member(
                eligibility_rules=eligibility_rules,
                user_jettons=user_jettons,
                user_nft_items=user_nft_items,
                chat_member=None,
            )
        )
        is_chat_member = telegram_chat_user_service.is_chat_member(
            chat_id=chat.id,
            user_id=user.id,
        )
        is_eligible = bool(eligibility_summary)

        return TelegramChatWithRulesFDO(
            chat=TelegramChatFDO(
                id=chat.id,
                username=chat.username,
                title=chat.title,
                slug=chat.slug,
                is_forum=chat.is_forum,
                logo_path=chat.logo_path,
                join_url=chat.invite_link if is_eligible else None,
                is_member=is_chat_member,
                is_eligible=is_eligible,
            ),
            rules=[
                TelegramChatEligibilityRuleFDO(
                    category=rule.category,
                    title=f"HOLD {rule.title}",
                    expected=rule.expected,
                    actual=rule.current,
                    is_eligible=rule.is_eligible,
                    photo_url=None,
                    blockchain_address=rule.address,
                )
                for rule in eligibility_summary.items
            ],
        )
