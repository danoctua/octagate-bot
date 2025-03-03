import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pytonapi.utils import userfriendly_to_raw
from sqlalchemy.exc import NoResultFound

from api.deps import validate_access_token
from api.pos.chat import (
    TelegramChatWithRulesFDO,
    TelegramChatFDO,
    TelegramChatEligibilityRuleFDO,
    BaseTelegramChatFDO,
    BaseTelegramChatEligibilityRuleFDO,
    AddChatCPO,
    ChatJettonRuleCPO,
    ToggleChatRuleCPO,
    TelegramChatCPO,
)
from core.actions.chat import (
    TelegramChatAction,
    TelegramChatAlreadyExists,
    TelegramChatNotSufficientPrivileges,
    TelegramChatNotExists,
)
from core.dtos.chat import TelegramChatEligibilitySummaryDTO, EligibilityCheckType
from core.services.chat import (
    TelegramChatService,
    TelegramChatUserService,
    TelegramChatJettonService,
)
from core.services.db import DBService
from core.services.nft import NftItemService
from core.services.user import UserService
from core.services.wallet import JettonWalletService

logger = logging.getLogger(__name__)

chat_router = APIRouter(prefix="/chats")


@chat_router.get("")
async def get_chats(
    user_id: int = Depends(validate_access_token),
) -> list[BaseTelegramChatFDO]:
    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        requestor = user_service.get(user_id)
        if not requestor.is_admin:
            raise HTTPException(
                detail={
                    "error": {"message": "You are not allowed to access this resource"}
                },
                status_code=403,
            )
        chat_service = TelegramChatService(db_session)
        chats = chat_service.get_all()

        return [
            BaseTelegramChatFDO(
                id=chat.id,
                username=chat.username,
                title=chat.title,
                description=chat.description,
                slug=chat.slug,
                is_forum=chat.is_forum,
                logo_path=chat.logo_path,
            )
            for chat in chats
        ]


@chat_router.post("")
async def create_chat(
    chat: AddChatCPO,
    user_id: int = Depends(validate_access_token),
) -> BaseTelegramChatFDO:
    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        requestor = user_service.get(user_id)
        if not requestor.is_admin:
            raise HTTPException(
                detail={
                    "error": {"message": "You are not allowed to access this resource"}
                },
                status_code=403,
            )

        logger.info(
            f"Creating chat {chat.chat_identifier!r} of type {type(chat.chat_identifier)}..."
        )

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
                detail={
                    "error": {"message": f"Chat '{chat.chat_identifier}' not found"}
                },
                status_code=400,
            )

        return telegram_chat


@chat_router.get("/{slug}")
async def get_chat(
    slug: str,
    params: Annotated[TelegramChatCPO, Query()],
    user_id: int = Depends(validate_access_token),
) -> TelegramChatWithRulesFDO:
    with DBService().db_session() as db_session:
        chat_service = TelegramChatService(db_session)
        try:
            chat = chat_service.get_by_slug(slug)
        except NoResultFound:
            logger.debug(f"Chat with slug {slug!r} not found")
            raise HTTPException(
                detail={"error": {"message": "Chat not found"}},
                status_code=404,
            )

        user_service = UserService(db_session)
        user = user_service.get(user_id)
        if params.full and not user.is_admin:
            raise HTTPException(
                detail={
                    "error": {"message": "You are not allowed to access this resource"}
                },
                status_code=403,
            )

        telegram_chat_user_service = TelegramChatUserService(db_session)
        eligibility_rules = telegram_chat_user_service.get_eligibility_rules(
            chat_id=chat.id,
            enabled_only=not params.full,
        )

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
                description=chat.description,
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
                    title=rule.title,
                    expected=rule.expected,
                    actual=rule.current,
                    is_eligible=rule.is_eligible,
                    photo_url=None,
                    blockchain_address=rule.address,
                    is_enabled=rule.is_enabled,
                )
                for rule in eligibility_summary.items
            ],
        )


@chat_router.get("/{slug}/rules/jettons/{address}")
async def get_chat_jetton_rule(
    slug: str,
    address: str,
    user_id: int = Depends(validate_access_token),
) -> BaseTelegramChatEligibilityRuleFDO:
    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        requestor = user_service.get(user_id)
        if not requestor.is_admin:
            raise HTTPException(
                detail={
                    "error": {"message": "You are not allowed to access this resource"}
                },
                status_code=403,
            )

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
            logger.debug(f"Rule for chat {chat.id!r} and jetton {address} not found")
            raise HTTPException(
                detail={"error": {"message": "Rule not found"}},
                status_code=404,
            )

        return BaseTelegramChatEligibilityRuleFDO(
            category=EligibilityCheckType.JETTON,
            title=rule.jetton.name,
            expected=rule.threshold,
            photo_url=rule.jetton.logo_path,
            blockchain_address=rule.jetton_address,
            is_enabled=rule.is_enabled,
        )


@chat_router.post("/{slug}/rules/jettons/{address}")
async def add_chat_jetton_rule(
    slug: str,
    address: str,
    rule: ChatJettonRuleCPO,
    user_id: int = Depends(validate_access_token),
) -> BaseTelegramChatEligibilityRuleFDO:
    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        requestor = user_service.get(user_id)
        if not requestor.is_admin:
            raise HTTPException(
                detail={
                    "error": {"message": "You are not allowed to access this resource"}
                },
                status_code=403,
            )

        telegram_chat_action = TelegramChatAction(db_session)
        result = telegram_chat_action.add_jetton_rule(
            slug=slug,
            address=address,
            expected=rule.expected,
        )
        return result


@chat_router.put("/{slug}/rules/jettons/{address}")
async def update_chat_jetton_rule(
    slug: str,
    address: str,
    rule: ChatJettonRuleCPO,
    user_id: int = Depends(validate_access_token),
) -> BaseTelegramChatEligibilityRuleFDO:
    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        requestor = user_service.get(user_id)
        if not requestor.is_admin:
            raise HTTPException(
                detail={
                    "error": {"message": "You are not allowed to access this resource"}
                },
                status_code=403,
            )

        telegram_chat_action = TelegramChatAction(db_session)
        result = telegram_chat_action.update_jetton_rule(
            slug=slug,
            address=address,
            expected=rule.expected,
        )
        return result


@chat_router.put("/{slug}/rules/jettons/{address}/toggle")
async def toggle_chat_jetton_rule(
    slug: str,
    address: str,
    rule: ToggleChatRuleCPO,
    user_id: int = Depends(validate_access_token),
) -> BaseTelegramChatEligibilityRuleFDO:
    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        requestor = user_service.get(user_id)
        if not requestor.is_admin:
            raise HTTPException(
                detail={
                    "error": {"message": "You are not allowed to access this resource"}
                },
                status_code=403,
            )

        telegram_chat_action = TelegramChatAction(db_session)
        result = telegram_chat_action.toggle_jetton_rule(
            slug=slug,
            address=address,
            is_enabled=rule.is_enabled,
        )
        return result
