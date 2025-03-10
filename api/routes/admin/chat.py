import logging

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from api.deps import get_db_session
from api.pos.chat import (
    TelegramChatJettonRuleCPO,
    AddChatCPO,
    TelegramChatNFTCollectionRuleCPO,
    BaseTelegramChatEligibilityRuleFDO,
    BaseTelegramChatFDO,
    TelegramChatWithRulesFDO,
)
from core.exceptions.chat import (
    TelegramChatNotSufficientPrivileges,
    TelegramChatAlreadyExists,
    TelegramChatNotExists,
)
from core.actions.chat.rule.blockchain import (
    TelegramChatNFTCollectionAction,
    TelegramChatJettonAction,
)
from core.actions.chat import TelegramChatAction
from core.services.chat import TelegramChatService

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
        result = await telegram_chat_action.get_with_eligibility_rules(slug=slug)
        return TelegramChatWithRulesFDO.from_dto(result)
    except TelegramChatNotExists:
        raise HTTPException(
            detail={"error": {"message": "Chat not found"}},
            status_code=404,
        )


@admin_chat_router.post("")
async def create_chat(
    chat: AddChatCPO,
    db_session: Session = Depends(get_db_session),
) -> BaseTelegramChatFDO:
    telegram_chat_action = TelegramChatAction(db_session)
    try:
        result = await telegram_chat_action.create(chat_identifier=chat.chat_identifier)
        return BaseTelegramChatFDO.model_validate(result.model_dump())
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


@admin_chat_router.get("/{slug}/rules/jettons/{rule_id}")
async def get_chat_jetton_rule(
    slug: str,
    rule_id: int,
    db_session: Session = Depends(get_db_session),
) -> BaseTelegramChatEligibilityRuleFDO:
    telegram_chat_jetton_action = TelegramChatJettonAction(db_session)
    return BaseTelegramChatEligibilityRuleFDO.model_validate(
        telegram_chat_jetton_action.read(rule_id=rule_id).model_dump()
    )


@admin_chat_router.post("/{slug}/rules/jettons")
async def add_chat_jetton_rule(
    slug: str,
    rule: TelegramChatJettonRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> BaseTelegramChatEligibilityRuleFDO:
    action = TelegramChatJettonAction(db_session)
    return BaseTelegramChatEligibilityRuleFDO.model_validate(
        action.create(
            slug=slug,
            address_raw=rule.address,
            threshold=rule.expected,
        ).model_dump()
    )


@admin_chat_router.put("/{slug}/rules/jettons/{rule_id}")
async def update_chat_jetton_rule(
    slug: str,
    rule_id: int,
    rule: TelegramChatJettonRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> BaseTelegramChatEligibilityRuleFDO:
    action = TelegramChatJettonAction(db_session)
    return BaseTelegramChatEligibilityRuleFDO.model_validate(
        action.update(
            rule_id=rule_id,
            address_raw=rule.address,
            expected=rule.expected,
            is_enabled=rule.is_enabled,
        ).model_dump()
    )


@admin_chat_router.get("/{slug}/rules/nft-collections/{rule_id}")
async def get_chat_nft_collection_rule(
    slug: str,
    rule_id: int,
    db_session: Session = Depends(get_db_session),
) -> BaseTelegramChatEligibilityRuleFDO:
    action = TelegramChatNFTCollectionAction(db_session)
    return BaseTelegramChatEligibilityRuleFDO.model_validate(
        action.read(rule_id=rule_id)
    )


@admin_chat_router.post("/{slug}/rules/nft-collections")
async def add_chat_nft_collection_rule(
    slug: str,
    rule: TelegramChatNFTCollectionRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> BaseTelegramChatEligibilityRuleFDO:
    action = TelegramChatNFTCollectionAction(db_session)
    return BaseTelegramChatEligibilityRuleFDO.model_validate(
        action.create(
            slug=slug,
            address_raw=rule.address,
            threshold=rule.expected,
        ).model_dump()
    )


@admin_chat_router.put("/{slug}/rules/nft-collections/{rule_id}")
async def update_chat_nft_collection_rule(
    slug: str,
    rule_id: int,
    rule: TelegramChatNFTCollectionRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> BaseTelegramChatEligibilityRuleFDO:
    action = TelegramChatNFTCollectionAction(db_session)
    return BaseTelegramChatEligibilityRuleFDO.model_validate(
        action.update(
            rule_id=rule_id,
            address_raw=rule.address,
            expected=rule.expected,
            is_enabled=rule.is_enabled,
        ).model_dump()
    )
