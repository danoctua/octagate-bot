import logging

from fastapi import APIRouter, HTTPException, Depends
from pytonapi.utils import userfriendly_to_raw
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from api.deps import get_db_session
from api.pos.chat import (
    BaseTelegramChatEligibilityRuleFDO,
    TelegramChatJettonRuleCPO,
    ToggleChatRuleCPO,
    AddChatCPO,
    BaseTelegramChatFDO,
    TelegramChatWithRulesFDO,
    TelegramChatNFTCollectionRuleCPO,
)
from core.actions.chat import (
    TelegramChatAction,
    TelegramChatAlreadyExists,
    TelegramChatNotSufficientPrivileges,
    TelegramChatNotExists,
    TelegramChatJettonAction,
    TelegramChatNFTCollectionAction,
)
from core.services.chat import TelegramChatService, TelegramChatJettonService

admin_chat_router = APIRouter(prefix="/chats")
logger = logging.getLogger(__name__)


@admin_chat_router.get("")
async def get_chats(
    db_session: Session = Depends(get_db_session),
) -> list[BaseTelegramChatFDO]:
    chat_service = TelegramChatService(db_session)
    chats = chat_service.get_all()

    return [BaseTelegramChatFDO.from_orm(chat) for chat in chats]


@admin_chat_router.get("/{slug}")
async def get_chat(
    slug: str,
    db_session: Session = Depends(get_db_session),
) -> TelegramChatWithRulesFDO:
    telegram_chat_action = TelegramChatAction(db_session)
    try:
        chat = await telegram_chat_action.get_with_eligibility_rules(slug=slug)
    except TelegramChatNotExists:
        raise HTTPException(
            detail={"error": {"message": "Chat not found"}},
            status_code=404,
        )
    return chat


@admin_chat_router.post("")
async def create_chat(
    chat: AddChatCPO,
    db_session: Session = Depends(get_db_session),
) -> BaseTelegramChatFDO:
    telegram_chat_action = TelegramChatAction(db_session)
    try:
        telegram_chat = await telegram_chat_action.create(
            chat_identifier=chat.chat_identifier
        )
    except TelegramChatAlreadyExists:
        raise HTTPException(
            detail={"error": {"message": "Chat already exists"}},
            status_code=409,
        )
    except TelegramChatNotSufficientPrivileges:
        raise HTTPException(
            detail={
                "error": {
                    "message": "You have to add bot to chat with admin rights to invite users first"
                }
            },
            status_code=409,
        )
    except TelegramChatNotExists:
        raise HTTPException(
            detail={"error": {"message": f"Chat '{chat.chat_identifier}' not found"}},
            status_code=400,
        )

    return telegram_chat


@admin_chat_router.get("/{slug}/rules/jettons/{address}")
async def get_chat_jetton_rule(
    slug: str,
    address: str,
    db_session: Session = Depends(get_db_session),
) -> BaseTelegramChatEligibilityRuleFDO:
    chat_service = TelegramChatService(db_session)
    try:
        chat = chat_service.get_by_slug(slug)
    except NoResultFound:
        logger.debug(f"Chat with slug {slug!r} not found")
        raise HTTPException(
            detail={"error": {"message": "Chat not found"}},
            status_code=404,
        )

    raw_address = userfriendly_to_raw(address)

    telegram_chat_jetton_service = TelegramChatJettonService(db_session)
    try:
        rule = telegram_chat_jetton_service.get(
            chat_id=chat.id, jetton_address=raw_address
        )
    except NoResultFound:
        logger.debug(f"Rule for chat {chat.id!r} and jetton {address!r} not found")
        raise HTTPException(
            detail={"error": {"message": "Rule not found"}},
            status_code=404,
        )

    return BaseTelegramChatEligibilityRuleFDO.from_jetton_rule(rule)


@admin_chat_router.post("/{slug}/rules/jettons/{address}")
async def add_chat_jetton_rule(
    slug: str,
    address: str,
    rule: TelegramChatJettonRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> BaseTelegramChatEligibilityRuleFDO:
    action = TelegramChatJettonAction(db_session)
    address_raw = userfriendly_to_raw(address)
    result = action.create(
        slug=slug,
        address_raw=address_raw,
        threshold=rule.expected,
    )
    return result


@admin_chat_router.put("/{slug}/rules/jettons/{address}")
async def update_chat_jetton_rule(
    slug: str,
    address: str,
    rule: TelegramChatJettonRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> BaseTelegramChatEligibilityRuleFDO:
    action = TelegramChatJettonAction(db_session)
    address_raw = userfriendly_to_raw(address)
    result = action.update(
        slug=slug,
        address_raw=address_raw,
        expected=rule.expected,
    )
    return result


@admin_chat_router.put("/{slug}/rules/jettons/{address}/toggle")
async def toggle_chat_jetton_rule(
    slug: str,
    address: str,
    rule: ToggleChatRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> BaseTelegramChatEligibilityRuleFDO:
    action = TelegramChatJettonAction(db_session)
    address_raw = userfriendly_to_raw(address)
    result = action.toggle(
        slug=slug,
        address_raw=address_raw,
        is_enabled=rule.is_enabled,
    )
    return result


@admin_chat_router.get("/{slug}/rules/nft-collections/{address}")
async def get_chat_nft_collection_rule(
    slug: str,
    address: str,
    db_session: Session = Depends(get_db_session),
) -> BaseTelegramChatEligibilityRuleFDO:
    action = TelegramChatNFTCollectionAction(db_session)
    return action.read(slug=slug, address_raw=userfriendly_to_raw(address))


@admin_chat_router.post("/{slug}/rules/nft-collections/{address}")
async def add_chat_nft_collection_rule(
    slug: str,
    address: str,
    rule: TelegramChatNFTCollectionRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> BaseTelegramChatEligibilityRuleFDO:
    action = TelegramChatNFTCollectionAction(db_session)
    return action.create(
        slug=slug,
        address_raw=userfriendly_to_raw(address),
        threshold=rule.expected,
    )
