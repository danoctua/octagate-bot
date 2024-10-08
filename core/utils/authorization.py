import logging

from telegram import ChatMember, ChatMemberAdministrator
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from core.models.user import User
from core.settings import Config


logger = logging.getLogger(__name__)


async def get_telegram_chat_member(
    context: ContextTypes.DEFAULT_TYPE, telegram_id: int
) -> ChatMember | None:
    try:
        chat_member = await context.bot.get_chat_member(
            chat_id=Config.TARGET_COMMON_CHAT_ID,
            user_id=telegram_id,
        )
        if chat_member is not None and chat_member.status in (ChatMember.LEFT,):
            return None

        return chat_member
    except TelegramError:
        logger.warning(f"Failed to get chat member for {telegram_id}")
        return None


async def get_telegram_chat_admins(
    context: ContextTypes.DEFAULT_TYPE,
) -> list[ChatMember]:
    return await context.bot.get_chat_administrators(
        chat_id=Config.TARGET_COMMON_CHAT_ID
    )


def get_user_from_chat_members(
    chat_members: list[ChatMember], telegram_id: int
) -> ChatMember | None:
    for chat_member in chat_members:
        if chat_member.user.id == telegram_id:
            return chat_member
    return None


def is_telegram_chat_whale_admin(chat_member: ChatMember) -> bool:
    """
    Check if the chat member is a whale admin
    :param chat_member: Chat member to check
    :return: bool - True if the chat member is a whale admin, False otherwise
    """
    if chat_member.status != ChatMember.ADMINISTRATOR or not isinstance(
        chat_member, ChatMemberAdministrator
    ):
        return False

    if chat_member.custom_title and chat_member.custom_title.startswith("8x"):
        return True

    return False


def is_telegram_chat_admin(chat_member: ChatMember | ChatMemberAdministrator) -> bool:
    """
    Check if the chat member is an admin that should never be demoted or banned
    :param chat_member: Chat member to check
    :return: bool
    """
    if chat_member.status not in (
        ChatMember.ADMINISTRATOR,
        ChatMember.OWNER,
    ):
        return False

    if not chat_member.custom_title or not chat_member.custom_title.startswith("8x"):
        return True

    return False


async def promote_user(
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
) -> None:
    if not (user.wallet and user.wallet.jetton_wallet):
        return

    # If user is not a whale, no need to promote
    if not user.wallet.jetton_wallet.is_whale:
        return

    chat_member = await get_telegram_chat_member(
        context=context, telegram_id=user.telegram_id
    )
    if not chat_member:
        logger.warning(
            f"Failed to promote user `{user.telegram_id}` to admin as chat member is not found"
        )
        return

    # If user is already an admin, no need to promote
    if chat_member.status in (ChatMember.ADMINISTRATOR, ChatMember.OWNER):
        logger.info(f"User `{user.telegram_id}` is already an admin")

        if is_telegram_chat_whale_admin(chat_member=chat_member):
            if chat_member.custom_title != f"8x{user.wallet.jetton_wallet.rating}":
                logger.info(
                    f"Updating admin title for user `{user.telegram_id}` to 8x{user.wallet.jetton_wallet.rating}"
                )
                await context.bot.set_chat_administrator_custom_title(
                    chat_id=Config.TARGET_COMMON_CHAT_ID,
                    user_id=user.telegram_id,
                    custom_title=f"8x{user.wallet.jetton_wallet.rating}",
                )

        return

    if chat_member.status == ChatMember.RESTRICTED:
        logger.info(f"User `{user.telegram_id}` is restricted")
        return

    logger.info(f"Promoting user `{user.telegram_id}` to admin")

    await context.bot.promote_chat_member(
        chat_id=Config.TARGET_COMMON_CHAT_ID,
        user_id=user.telegram_id,
        can_manage_topics=True,
    )
    await context.bot.set_chat_administrator_custom_title(
        chat_id=Config.TARGET_COMMON_CHAT_ID,
        user_id=user.telegram_id,
        custom_title=f"8x{user.wallet.jetton_wallet.rating}",
    )
    await context.bot.send_message(
        chat_id=user.telegram_id,
        text=(
            f"You've been promoted to admins in the chat as you're whale #{user.wallet.jetton_wallet.rating}!"
        ),
    )


async def demote_user(context: ContextTypes.DEFAULT_TYPE, telegram_id: int) -> None:
    chat_member = await get_telegram_chat_member(
        context=context, telegram_id=telegram_id
    )

    if not chat_member:
        return

    if not is_telegram_chat_whale_admin(chat_member=chat_member):
        return

    logger.info(f"Demoting user `{telegram_id}` from admin")

    await context.bot.promote_chat_member(
        chat_id=Config.TARGET_COMMON_CHAT_ID,
        user_id=telegram_id,
        can_manage_topics=False,
    )
    await context.bot.send_message(
        chat_id=telegram_id,
        text="You've been demoted from admins in the chat as you lost your whale status!",
    )
