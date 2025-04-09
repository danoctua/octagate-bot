import logging

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from starlette.status import HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST

from api.deps import get_db_session
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
    TelegramChatToncoinRuleCPO,
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
    TelegramChatToncoinAction,
)
from core.actions.chat import TelegramChatAction, TelegramChatManageAction
from core.services.chat import TelegramChatService

admin_chat_router = APIRouter(prefix="/chats")
logger = logging.getLogger(__name__)


@admin_chat_router.get(
    "",
    description="Get all chats managed by the current user - all chats where user is admin",
    tags=["Chat management"],
)
async def get_chats(
    request: Request,
    db_session: Session = Depends(get_db_session),
) -> list[BaseTelegramChatFDO]:
    chat_service = TelegramChatService(db_session)
    if request.state.user.is_admin:
        chats = chat_service.get_all()
    else:
        chats = chat_service.get_all_managed(user_id=request.state.user.id)

    return [BaseTelegramChatFDO.from_orm(chat) for chat in chats]


@admin_chat_router.get(
    "/{slug}", description="Get specific chat details", tags=["Chat management"]
)
async def get_chat(
    request: Request,
    slug: str,
    db_session: Session = Depends(get_db_session),
) -> TelegramChatWithRulesFDO:
    telegram_chat_action = TelegramChatManageAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    result = await telegram_chat_action.get_with_eligibility_rules()
    return TelegramChatWithRulesFDO.from_dto(result)


@admin_chat_router.post("", deprecated=True, tags=["Chat management"])
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
            detail="Chat already exists",
            status_code=HTTP_409_CONFLICT,
        )
    except TelegramChatNotSufficientPrivileges:
        raise HTTPException(
            detail="You have to add bot to chat with admin rights to invite users first",
            status_code=HTTP_400_BAD_REQUEST,
        )
    except TelegramChatNotExists:
        raise HTTPException(
            detail=f"Chat '{chat.chat_identifier}' not found",
            status_code=HTTP_400_BAD_REQUEST,
        )


@admin_chat_router.post(
    "/{slug}/refresh",
    description="Refreshes chat details, like logo. Normally not needed and is more like an emergency endpoint.",
    tags=["Chat management"],
)
async def refresh_chat(
    request: Request,
    slug: str,
    db_session: Session = Depends(get_db_session),
) -> BaseTelegramChatFDO:
    action = TelegramChatManageAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    try:
        result = await action.refresh()
        return BaseTelegramChatFDO.model_validate(result.model_dump())
    except TelegramChatNotSufficientPrivileges:
        raise HTTPException(
            detail="You have to add bot to chat with admin rights to invite users first",
            status_code=HTTP_400_BAD_REQUEST,
        )


@admin_chat_router.put("/{slug}", tags=["Chat management"])
async def update_chat(
    request: Request,
    slug: str,
    chat: EditChatCPO,
    db_session: Session = Depends(get_db_session),
) -> BaseTelegramChatFDO:
    telegram_chat_action = TelegramChatManageAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    result = await telegram_chat_action.update(description=chat.description)
    return BaseTelegramChatFDO.model_validate(result.model_dump())


@admin_chat_router.delete(
    "/{slug}",
    deprecated=True,
    tags=["Chat management"],
)
async def delete_chat(
    request: Request,
    slug: str,
    db_session: Session = Depends(get_db_session),
) -> None:
    telegram_chat_action = TelegramChatManageAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    await telegram_chat_action.delete()


@admin_chat_router.get("/{slug}/rules/toncoin/{rule_id}", tags=["Rules"])
async def get_chat_toncoin_rule(
    request: Request,
    slug: str,
    rule_id: int,
    db_session: Session = Depends(get_db_session),
) -> ChatEligibilityRuleFDO:
    telegram_chat_toncoin_action = TelegramChatToncoinAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    return ChatEligibilityRuleFDO.model_validate(
        telegram_chat_toncoin_action.read(rule_id=rule_id).model_dump()
    )


@admin_chat_router.post("/{slug}/rules/toncoin", tags=["Rules"])
async def add_chat_toncoin_rule(
    request: Request,
    slug: str,
    rule: TelegramChatToncoinRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> ChatEligibilityRuleFDO:
    telegram_chat_toncoin_action = TelegramChatToncoinAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    return ChatEligibilityRuleFDO.model_validate(
        telegram_chat_toncoin_action.create(
            threshold=rule.expected,
        ).model_dump()
    )


@admin_chat_router.put("/{slug}/rules/toncoin/{rule_id}", tags=["Rules"])
async def update_chat_toncoin_rule(
    request: Request,
    slug: str,
    rule_id: int,
    rule: TelegramChatToncoinRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> ChatEligibilityRuleFDO:
    telegram_chat_toncoin_action = TelegramChatToncoinAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    return ChatEligibilityRuleFDO.model_validate(
        telegram_chat_toncoin_action.update(
            rule_id=rule_id,
            threshold=rule.expected,
            is_enabled=rule.is_enabled,
        ).model_dump()
    )


@admin_chat_router.delete("/{slug}/rules/toncoin/{rule_id}", tags=["Rules"])
async def delete_chat_toncoin_rule(
    request: Request,
    slug: str,
    rule_id: int,
    db_session: Session = Depends(get_db_session),
) -> None:
    telegram_chat_toncoin_action = TelegramChatToncoinAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    telegram_chat_toncoin_action.delete(rule_id=rule_id)


@admin_chat_router.get("/{slug}/rules/jettons/{rule_id}", tags=["Rules"])
async def get_chat_jetton_rule(
    request: Request,
    slug: str,
    rule_id: int,
    db_session: Session = Depends(get_db_session),
) -> ChatEligibilityRuleFDO:
    telegram_chat_jetton_action = TelegramChatJettonAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    return ChatEligibilityRuleFDO.model_validate(
        telegram_chat_jetton_action.read(rule_id=rule_id).model_dump()
    )


@admin_chat_router.post("/{slug}/rules/jettons", tags=["Rules"])
async def add_chat_jetton_rule(
    request: Request,
    slug: str,
    rule: TelegramChatJettonRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> ChatEligibilityRuleFDO:
    telegram_chat_jetton_action = TelegramChatJettonAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    chat_jetton_rule = await telegram_chat_jetton_action.create(
        address_raw=rule.address,
        threshold=rule.expected,
    )
    return ChatEligibilityRuleFDO.model_validate(chat_jetton_rule.model_dump())


@admin_chat_router.put("/{slug}/rules/jettons/{rule_id}", tags=["Rules"])
async def update_chat_jetton_rule(
    request: Request,
    slug: str,
    rule_id: int,
    rule: TelegramChatJettonRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> ChatEligibilityRuleFDO:
    action = TelegramChatJettonAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    chat_jetton_rule = await action.update(
        rule_id=rule_id,
        address_raw=rule.address,
        expected=rule.expected,
        is_enabled=rule.is_enabled,
    )
    return ChatEligibilityRuleFDO.model_validate(chat_jetton_rule.model_dump())


@admin_chat_router.delete("/{slug}/rules/jettons/{rule_id}", tags=["Rules"])
async def delete_chat_jetton_rule(
    request: Request,
    slug: str,
    rule_id: int,
    db_session: Session = Depends(get_db_session),
) -> None:
    action = TelegramChatJettonAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    await action.delete(rule_id=rule_id)


@admin_chat_router.get("/{slug}/rules/nft-collections/{rule_id}", tags=["Rules"])
async def get_chat_nft_collection_rule(
    request: Request,
    slug: str,
    rule_id: int,
    db_session: Session = Depends(get_db_session),
) -> NftEligibilityRuleFDO:
    action = TelegramChatNFTCollectionAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    return NftEligibilityRuleFDO.model_validate(
        action.read(rule_id=rule_id).model_dump()
    )


@admin_chat_router.post("/{slug}/rules/nft-collections", tags=["Rules"])
async def add_chat_nft_collection_rule(
    request: Request,
    slug: str,
    rule: TelegramChatNFTCollectionRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> NftEligibilityRuleFDO:
    action = TelegramChatNFTCollectionAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    chat_nft_collection_rule = await action.create(
        address_raw=rule.address,
        threshold=rule.expected,
        required_attributes=rule.required_attributes,
    )
    return NftEligibilityRuleFDO.model_validate(chat_nft_collection_rule.model_dump())


@admin_chat_router.put("/{slug}/rules/nft-collections/{rule_id}", tags=["Rules"])
async def update_chat_nft_collection_rule(
    request: Request,
    slug: str,
    rule_id: int,
    rule: TelegramChatNFTCollectionRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> NftEligibilityRuleFDO:
    action = TelegramChatNFTCollectionAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    nft_collection_rule = await action.update(
        rule_id=rule_id,
        address_raw=rule.address,
        expected=rule.expected,
        is_enabled=rule.is_enabled,
        required_attributes=rule.required_attributes,
    )
    return NftEligibilityRuleFDO.model_validate(nft_collection_rule.model_dump())


@admin_chat_router.delete("/{slug}/rules/nft-collections/{rule_id}", tags=["Rules"])
async def delete_chat_nft_collection_rule(
    request: Request,
    slug: str,
    rule_id: int,
    db_session: Session = Depends(get_db_session),
) -> None:
    action = TelegramChatNFTCollectionAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    await action.delete(rule_id=rule_id)


@admin_chat_router.post("/{slug}/rules/whitelist", tags=["Rules"])
async def add_chat_whitelist_rule(
    request: Request,
    slug: str,
    rule: CreateWhitelistRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> WhitelistRuleFDO:
    action = TelegramChatWhitelistAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    new_rule = action.create(
        name=rule.name,
        description=rule.description,
    )
    result = await action.set_content(
        rule_id=new_rule.id,
        content=rule.users,
    )
    return WhitelistRuleFDO.model_validate(result.model_dump())


@admin_chat_router.put("/{slug}/rules/whitelist/{rule_id}", tags=["Rules"])
async def update_chat_whitelist_rule(
    request: Request,
    slug: str,
    rule_id: int,
    rule: UpdateWhitelistRuleCPO,
    db_session: Session = Depends(get_db_session),
) -> WhitelistRuleFDO:
    action = TelegramChatWhitelistAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    action.update(
        rule_id=rule_id,
        name=rule.name,
        description=rule.description,
        is_enabled=rule.is_enabled,
    )
    result = await action.set_content(rule_id=rule_id, content=rule.users)
    return WhitelistRuleFDO.model_validate(result.model_dump())


@admin_chat_router.delete("/{slug}/rules/whitelist/{rule_id}", tags=["Rules"])
async def delete_chat_whitelist_rule(
    request: Request,
    slug: str,
    rule_id: int,
    db_session: Session = Depends(get_db_session),
) -> None:
    action = TelegramChatWhitelistAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    await action.delete(rule_id=rule_id)


@admin_chat_router.get("/{slug}/rules/whitelist/{rule_id}", tags=["Rules"])
async def get_chat_whitelist_rule(
    request: Request,
    slug: str,
    rule_id: int,
    db_session: Session = Depends(get_db_session),
) -> WhitelistRuleFDO:
    action = TelegramChatWhitelistAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    result = action.get(
        rule_id=rule_id,
    )
    return WhitelistRuleFDO.model_validate(result.model_dump())


@admin_chat_router.post("/{slug}/rules/whitelist-external", tags=["Rules"])
async def add_chat_whitelist_external_source_rule(
    request: Request,
    slug: str,
    rule: CreateWhitelistRuleExternalCPO,
    db_session: Session = Depends(get_db_session),
) -> WhitelistRuleExternalFDO:
    action = TelegramChatWhitelistExternalSourceAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    try:
        new_rule = await action.create(
            name=rule.name,
            description=rule.description,
            external_source_url=str(rule.url),
        )
    except Exception as e:
        logger.error("Failed to create whitelist external source", exc_info=e)
        raise HTTPException(
            detail="Failed to create whitelist external source",
            status_code=HTTP_400_BAD_REQUEST,
        )
    return WhitelistRuleExternalFDO.model_validate(new_rule.model_dump())


@admin_chat_router.get("/{slug}/rules/whitelist-external/{rule_id}", tags=["Rules"])
async def get_chat_whitelist_external_source_rule(
    request: Request,
    slug: str,
    rule_id: int,
    db_session: Session = Depends(get_db_session),
) -> WhitelistRuleExternalFDO:
    action = TelegramChatWhitelistExternalSourceAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    result = action.get(rule_id=rule_id)
    return WhitelistRuleExternalFDO.model_validate(result.model_dump())


@admin_chat_router.put("/{slug}/rules/whitelist-external/{rule_id}", tags=["Rules"])
async def update_chat_whitelist_external_source_rule(
    request: Request,
    slug: str,
    rule_id: int,
    rule: UpdateWhitelistRuleExternalCPO,
    db_session: Session = Depends(get_db_session),
) -> WhitelistRuleExternalFDO:
    action = TelegramChatWhitelistExternalSourceAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
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
            detail="Failed to update whitelist external source",
            status_code=HTTP_400_BAD_REQUEST,
        )

    result = action.get(rule_id=rule_id)
    return WhitelistRuleExternalFDO.model_validate(result.model_dump())


@admin_chat_router.delete("/{slug}/rules/whitelist-external/{rule_id}", tags=["Rules"])
async def delete_chat_whitelist_external_source_rule(
    request: Request,
    slug: str,
    rule_id: int,
    db_session: Session = Depends(get_db_session),
) -> None:
    action = TelegramChatWhitelistExternalSourceAction(
        db_session=db_session,
        requestor=request.state.user,
        chat_slug=slug,
    )
    await action.delete(rule_id=rule_id)
