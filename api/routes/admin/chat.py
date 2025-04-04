import logging

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from api.deps import get_db_session, validate_access_token
from api.pos.chat import (
    TelegramChatJettonRuleCPO,
    AddChatCPO,
    TelegramChatNFTCollectionRuleCPO,
    ChatEligibilityRuleFDO,
    BaseTelegramChatFDO,
    TelegramChatWithRulesFDO,
    CreateWhitelistRuleCPO,
    WhitelistRuleFDO,
    UpdateWhitelistRuleCPO,
    WhitelistRuleExternalFDO,
    CreateWhitelistRuleExternalCPO,
    UpdateWhitelistRuleExternalCPO,
    EditChatCPO,
    NftEligibilityRuleFDO,
)
from core.actions.chat.rule.whitelist import (
    TelegramChatWhitelistAction,
    TelegramChatWhitelistExternalSourceAction,
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
from core.models.user import User
from core.services.chat import TelegramChatService

admin_chat_router = APIRouter(prefix="/chats")
logger = logging.getLogger(__name__)


@admin_chat_router.get(
    "",
    description="Get all chats managed by the current user - all chats where user is admin",
)
async def get_chats(
    db_session: Session = Depends(get_db_session),
    user: User = Depends(validate_access_token),
) -> list[BaseTelegramChatFDO]:
    chat_service = TelegramChatService(db_session)
    if user.is_admin:
        chats = chat_service.get_all()
    else:
        chats = chat_service.get_all_managed(user_id=user.id)

    return [BaseTelegramChatFDO.from_orm(chat) for chat in chats]


@admin_chat_router.get("/{slug}", description="Get specific chat details")
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


@admin_chat_router.post("", deprecated=True)
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
            status_code=400,
        )
    except TelegramChatNotExists:
        raise HTTPException(
            detail={"error": {"message": f"Chat '{chat.chat_identifier}' not found"}},
            status_code=400,
        )


@admin_chat_router.post(
    "/{slug}/refresh",
    description="Refreshes chat details, like logo. Normally not needed and is more like an emergency endpoint.",
)
async def refresh_chat(
    slug: str,
    db_session: Session = Depends(get_db_session),
) -> BaseTelegramChatFDO:
    telegram_chat_action = TelegramChatAction(db_session)
    try:
        result = await telegram_chat_action.refresh(slug=slug)
        return BaseTelegramChatFDO.model_validate(result.model_dump())
    except TelegramChatNotExists:
        raise HTTPException(
            detail={"error": {"message": "Chat not found"}},
            status_code=404,
        )
    except TelegramChatNotSufficientPrivileges:
        raise HTTPException(
            detail={
                "error": {
                    "message": "You have to add bot to chat with admin rights to invite users first"
                }
            },
            status_code=400,
        )


@admin_chat_router.put("/{slug}")
async def update_chat(
    slug: str,
    chat: EditChatCPO,
    db_session: Session = Depends(get_db_session),
) -> BaseTelegramChatFDO:
    telegram_chat_action = TelegramChatAction(db_session)
    try:
        result = await telegram_chat_action.update(
            slug=slug, description=chat.description
        )
        return BaseTelegramChatFDO.model_validate(result.model_dump())
    except TelegramChatNotExists:
        raise HTTPException(
            detail={"error": {"message": "Chat not found"}},
            status_code=404,
        )


@admin_chat_router.delete(
    "/{slug}",
    deprecated=True,
)
async def delete_chat(
    slug: str,
    db_session: Session = Depends(get_db_session),
) -> None:
    telegram_chat_action = TelegramChatAction(db_session)
    try:
        await telegram_chat_action.delete(slug=slug)
    except TelegramChatNotExists:
        raise HTTPException(
            detail={"error": {"message": "Chat not found"}},
            status_code=404,
        )


@admin_chat_router.get("/{slug}/rules/jettons/{rule_id}")
async def get_chat_jetton_rule(
    slug: str,
    rule_id: int,
    db_session: Session = Depends(get_db_session),
) -> ChatEligibilityRuleFDO:
    telegram_chat_jetton_action = TelegramChatJettonAction(db_session)
    return ChatEligibilityRuleFDO.model_validate(
        telegram_chat_jetton_action.read(rule_id=rule_id).model_dump()
    )


@admin_chat_router.post("/{slug}/rules/jettons")
async def add_chat_jetton_rule(
    slug: str,
    rule: TelegramChatJettonRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> ChatEligibilityRuleFDO:
    telegram_chat_jetton_action = TelegramChatJettonAction(db_session)
    chat_jetton_rule = await telegram_chat_jetton_action.create(
        slug=slug,
        address_raw=rule.address,
        threshold=rule.expected,
    )
    return ChatEligibilityRuleFDO.model_validate(chat_jetton_rule.model_dump())


@admin_chat_router.put("/{slug}/rules/jettons/{rule_id}")
async def update_chat_jetton_rule(
    slug: str,
    rule_id: int,
    rule: TelegramChatJettonRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> ChatEligibilityRuleFDO:
    action = TelegramChatJettonAction(db_session)
    chat_jetton_rule = await action.update(
        rule_id=rule_id,
        address_raw=rule.address,
        expected=rule.expected,
        is_enabled=rule.is_enabled,
    )
    return ChatEligibilityRuleFDO.model_validate(chat_jetton_rule.model_dump())


@admin_chat_router.get("/{slug}/rules/nft-collections/{rule_id}")
async def get_chat_nft_collection_rule(
    slug: str,
    rule_id: int,
    db_session: Session = Depends(get_db_session),
) -> NftEligibilityRuleFDO:
    action = TelegramChatNFTCollectionAction(db_session)
    return NftEligibilityRuleFDO.model_validate(
        action.read(rule_id=rule_id).model_dump()
    )


@admin_chat_router.post("/{slug}/rules/nft-collections")
async def add_chat_nft_collection_rule(
    slug: str,
    rule: TelegramChatNFTCollectionRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> NftEligibilityRuleFDO:
    action = TelegramChatNFTCollectionAction(db_session)
    chat_nft_collection_rule = await action.create(
        slug=slug,
        address_raw=rule.address,
        threshold=rule.expected,
        required_attributes=rule.required_attributes,
    )
    return NftEligibilityRuleFDO.model_validate(chat_nft_collection_rule.model_dump())


@admin_chat_router.put("/{slug}/rules/nft-collections/{rule_id}")
async def update_chat_nft_collection_rule(
    slug: str,
    rule_id: int,
    rule: TelegramChatNFTCollectionRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> NftEligibilityRuleFDO:
    action = TelegramChatNFTCollectionAction(db_session)
    nft_collection_rule = await action.update(
        rule_id=rule_id,
        address_raw=rule.address,
        expected=rule.expected,
        is_enabled=rule.is_enabled,
        required_attributes=rule.required_attributes,
    )
    return NftEligibilityRuleFDO.model_validate(nft_collection_rule.model_dump())


@admin_chat_router.post("/{slug}/rules/whitelist")
async def add_chat_whitelist_rule(
    slug: str,
    rule: CreateWhitelistRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> WhitelistRuleFDO:
    action = TelegramChatWhitelistAction(db_session)
    new_rule = action.create(
        slug=slug,
        name=rule.name,
        description=rule.description,
    )
    result = await action.set_content(new_rule.id, rule.users)
    return WhitelistRuleFDO.model_validate(result.model_dump())


@admin_chat_router.put("/{slug}/rules/whitelist/{rule_id}")
async def update_chat_whitelist_rule(
    slug: str,
    rule_id: int,
    rule: UpdateWhitelistRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> WhitelistRuleFDO:
    action = TelegramChatWhitelistAction(db_session)
    action.update(
        rule_id=rule_id,
        name=rule.name,
        description=rule.description,
        is_enabled=rule.is_enabled,
    )
    result = await action.set_content(rule_id, rule.users)
    return WhitelistRuleFDO.model_validate(result.model_dump())


@admin_chat_router.get("/{slug}/rules/whitelist/{rule_id}")
async def get_chat_whitelist_rule(
    slug: str,
    rule_id: int,
    db_session: Session = Depends(get_db_session),
) -> WhitelistRuleFDO:
    action = TelegramChatWhitelistAction(db_session)
    result = action.get(rule_id=rule_id)
    return WhitelistRuleFDO.model_validate(result.model_dump())


@admin_chat_router.post("/{slug}/rules/whitelist-external")
async def add_chat_whitelist_external_source_rule(
    slug: str,
    rule: CreateWhitelistRuleExternalCPO,
    db_session: Session = Depends(get_db_session),
) -> WhitelistRuleExternalFDO:
    action = TelegramChatWhitelistExternalSourceAction(db_session)
    try:
        new_rule = await action.create(
            slug=slug,
            name=rule.name,
            description=rule.description,
            external_source_url=str(rule.url),
        )
    except Exception as e:
        logger.error("Failed to create whitelist external source", exc_info=e)
        raise HTTPException(
            detail={"error": {"message": "Failed to create whitelist external source"}},
            status_code=400,
        )
    return WhitelistRuleExternalFDO.model_validate(new_rule.model_dump())


@admin_chat_router.get("/{slug}/rules/whitelist-external/{rule_id}")
async def get_chat_whitelist_external_source_rule(
    slug: str,
    rule_id: int,
    db_session: Session = Depends(get_db_session),
) -> WhitelistRuleExternalFDO:
    action = TelegramChatWhitelistExternalSourceAction(db_session)
    result = action.get(rule_id=rule_id)
    return WhitelistRuleExternalFDO.model_validate(result.model_dump())


@admin_chat_router.put("/{slug}/rules/whitelist-external/{rule_id}")
async def update_chat_whitelist_external_source_rule(
    slug: str,
    rule_id: int,
    rule: UpdateWhitelistRuleExternalCPO,
    db_session: Session = Depends(get_db_session),
) -> WhitelistRuleExternalFDO:
    action = TelegramChatWhitelistExternalSourceAction(db_session)
    try:
        await action.update(
            rule_id=rule_id,
            name=rule.name,
            description=rule.description,
            external_source_url=str(rule.url),
            is_enabled=rule.is_enabled,
        )
    except Exception as e:
        logger.error("Failed to update whitelist external source", exc_info=e)
        raise HTTPException(
            detail={"error": {"message": "Failed to update whitelist external source"}},
            status_code=400,
        )

    result = action.get(rule_id=rule_id)
    return WhitelistRuleExternalFDO.model_validate(result.model_dump())
