import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import validate_access_token, get_db_session
from api.pos.chat import (
    TelegramChatWithRulesFDO,
)
from core.actions.chat import TelegramChatAction, TelegramChatNotExists
from core.models.user import User

logger = logging.getLogger(__name__)

chat_router = APIRouter(prefix="/chats")


@chat_router.get("/{slug}")
async def get_chat(
    slug: str,
    user: User = Depends(validate_access_token),
    db_session: Session = Depends(get_db_session),
) -> TelegramChatWithRulesFDO:
    telegram_chat_action = TelegramChatAction(db_session)
    try:
        return await telegram_chat_action.get_with_eligibility_summary(
            slug=slug,
            user=user,
        )
    except TelegramChatNotExists:
        raise HTTPException(
            detail={"error": {"message": "Chat not found"}},
            status_code=404,
        )
