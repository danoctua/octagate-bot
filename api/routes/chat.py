import logging

from fastapi import APIRouter
from pytonapi.utils import raw_to_userfriendly
from sqlalchemy.exc import NoResultFound

from api.pos.chat import (
    TelegramChatWithRulesFDO,
    TelegramChatFDO,
    TelegramChatEligibilityRuleFDO,
    PROMOTE_JETTON_TEMPLATE,
    PROMOTE_NFT_COLLECTION_TEMPLATE,
)
from core.dtos.chat import EligibilityCheckType
from core.services.chat import TelegramChatService, TelegramChatUserService
from core.services.db import DBService


logger = logging.getLogger(__name__)

chat_router = APIRouter(prefix="/chats")


@chat_router.get("/{slug}")
async def get_chat(slug: str) -> TelegramChatWithRulesFDO:
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

        return TelegramChatWithRulesFDO(
            chat=TelegramChatFDO(
                id=chat.id,
                username=chat.username,
                title=chat.title,
                slug=chat.slug,
                is_forum=chat.is_forum,
                logo_path=chat.logo_path,
            ),
            rules=[
                *[
                    TelegramChatEligibilityRuleFDO(
                        category=EligibilityCheckType.JETTON,
                        title=f"HOLD {rule.jetton.name}",
                        promote_url=PROMOTE_JETTON_TEMPLATE.format(
                            jetton_master_address=raw_to_userfriendly(
                                rule.jetton_address
                            )
                        ),
                        expected=rule.threshold,
                        photo_url=rule.jetton.logo_path,
                    )
                    for rule in eligibility_rules.jettons
                ],
                *[
                    TelegramChatEligibilityRuleFDO(
                        category=EligibilityCheckType.NFT_COLLECTION,
                        title=f"HOLD {rule.nft_collection.name}",
                        promote_url=PROMOTE_NFT_COLLECTION_TEMPLATE.format(
                            collection_address=raw_to_userfriendly(
                                rule.collection_address
                            )
                        ),
                        expected=1,
                        photo_url=rule.nft_collection.logo_path,
                    )
                    for rule in eligibility_rules.nft_collections
                ],
            ],
        )
