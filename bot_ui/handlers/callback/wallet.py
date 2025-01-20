import asyncio
import datetime
import logging
from io import BytesIO

import qrcode
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from core.actions.wallet import WalletAction
from core.constants import DEFAULT_CONNECT_TIMEOUT
from core.dtos.user import TelegramUserDTO
from bot_ui.renderers import MAIN_BUTTON_REPLY_MARKUP, connected_wallet_response
from core.services.db import DBService
from core.services.storage import get_connector
from core.services.user import UserService
from core.services.wallet import WalletService, UserWalletExistError
from bot_ui.utils import delete_message

logger = logging.Logger(__name__)


async def connect_wallet_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await update.callback_query.answer()
    connector = get_connector(chat_id=update.effective_chat.id)
    is_connected = connector.connected
    if is_connected:
        with DBService().db_session() as db_session:
            user_service = UserService(db_session)
            user = user_service.get_or_create(
                telegram_user=TelegramUserDTO(
                    id=update.effective_user.id,
                    first_name=update.effective_user.first_name,
                    last_name=update.effective_user.last_name,
                    username=update.effective_user.username,
                    is_premium=update.effective_user.is_premium or False,
                    language_code=update.effective_user.language_code,
                )
            )
            if user.wallet:
                await connected_wallet_response(
                    db_session=db_session,
                    user=user,
                    context=context,
                    update=update,
                )
                return await delete_message(
                    context=context,
                    chat_id=update.effective_chat.id,
                    message_id=update.effective_message.message_id,
                )
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Wallet is already connected! There might be some error, however",
                    reply_markup=MAIN_BUTTON_REPLY_MARKUP,
                )
                await delete_message(
                    context=context,
                    chat_id=update.effective_chat.id,
                    message_id=update.effective_message.message_id,
                )
                return

    wallet_name = update.callback_query.data.split(":")[1]
    wallets_list = connector.get_wallets()
    wallet = next(filter(lambda w: w["name"] == wallet_name, wallets_list), None)
    if not wallet:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Unknown wallet type!",
            reply_markup=MAIN_BUTTON_REPLY_MARKUP,
        )
        await delete_message(
            context=context,
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id,
        )
        return

    generated_url = await connector.connect(wallet)

    reply_markup = InlineKeyboardMarkup.from_column(
        [InlineKeyboardButton(text="Connect", url=generated_url)]
    )

    img = qrcode.make(generated_url)
    stream = BytesIO()
    img.save(stream)
    message = await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=stream.getvalue(),
        caption="Connect wallet within 3 minutes",
        reply_markup=reply_markup,
    )
    await delete_message(
        context=context,
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id,
    )

    start_time = datetime.datetime.now()
    for i in range(DEFAULT_CONNECT_TIMEOUT + 1):
        if (datetime.datetime.now() - start_time).seconds >= DEFAULT_CONNECT_TIMEOUT:
            if connector.connected:
                await connector.disconnect()
            break
        await asyncio.sleep(1)

        if connector.connected:
            if connector.account.address:
                with DBService().db_session() as db_session:
                    user_service = UserService(db_session)
                    user = user_service.get_or_create(
                        telegram_user=TelegramUserDTO(
                            id=update.effective_user.id,
                            first_name=update.effective_user.first_name,
                            last_name=update.effective_user.last_name,
                            username=update.effective_user.username,
                            is_premium=update.effective_user.is_premium or False,
                            language_code=update.effective_user.language_code,
                        )
                    )
                    wallet_action = WalletAction(db_session)
                    try:
                        wallet_action.connect_wallet(
                            user_id=user.id,
                            wallet_address=connector.account.address,
                        )
                    except UserWalletExistError:
                        await connector.disconnect()
                        await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text="Wallet is already connected to another account!",
                            reply_markup=MAIN_BUTTON_REPLY_MARKUP,
                        )
                        await delete_message(
                            context=context,
                            chat_id=update.effective_chat.id,
                            message_id=message.message_id,
                        )
                        return
                    except Exception as e:
                        logger.error(
                            f"Error while connecting wallet: {e}", exc_info=True
                        )
                        await connector.disconnect()
                        await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text="Error while connecting wallet!",
                            reply_markup=MAIN_BUTTON_REPLY_MARKUP,
                        )
                        await delete_message(
                            context=context,
                            chat_id=update.effective_chat.id,
                            message_id=message.message_id,
                        )
                        return

                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="Wallet connected successfully!",
                    )
                    await delete_message(
                        context=context,
                        chat_id=update.effective_chat.id,
                        message_id=message.message_id,
                    )
                    connector.pause_connection()

                    return await connected_wallet_response(
                        db_session=db_session,
                        user=user,
                        context=context,
                        update=update,
                    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Connection timeout!",
        reply_markup=MAIN_BUTTON_REPLY_MARKUP,
    )
    return await delete_message(
        context=context,
        chat_id=update.effective_chat.id,
        message_id=message.message_id,
    )


async def disconnect_wallet_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await update.callback_query.answer()
    connector = get_connector(chat_id=update.effective_chat.id)
    await connector.restore_connection()

    with DBService().db_session() as db_session:
        wallet_action = WalletAction(db_session)
        await wallet_action.disconnect_wallet(telegram_id=update.effective_user.id)

        if connector.connected:
            await connector.disconnect()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Wallet disconnected successfully!",
        reply_markup=MAIN_BUTTON_REPLY_MARKUP,
    )
    return await delete_message(
        context, update.effective_chat.id, update.effective_message.message_id
    )


async def show_wallet_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await update.callback_query.answer()
    logger.info(f"User {update.effective_user.id!r} shows wallet")
    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        user = user_service.get_or_create(
            telegram_user=TelegramUserDTO(
                id=update.effective_user.id,
                first_name=update.effective_user.first_name,
                last_name=update.effective_user.last_name,
                username=update.effective_user.username,
                is_premium=update.effective_user.is_premium or False,
                language_code=update.effective_user.language_code,
            )
        )
        if user.wallet:
            wallet_service = WalletService(db_session)
            if user.wallet.hide_wallet:
                wallet_service.turn_visibility_on(user_id=user.id)
                # db_session.refresh(user)
                # await promote_user(context=context, user=user)
                return await connected_wallet_response(
                    db_session=db_session,
                    user=user,
                    context=context,
                    update=update,
                )
        else:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=update.effective_message.message_id,
                text="Wallet is not connected!",
                reply_markup=MAIN_BUTTON_REPLY_MARKUP,
            )


async def hide_wallet_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await update.callback_query.answer()
    logger.info(f"User {update.effective_user.id!r} hides wallet")
    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        user = user_service.get_or_create(
            telegram_user=TelegramUserDTO(
                id=update.effective_user.id,
                first_name=update.effective_user.first_name,
                last_name=update.effective_user.last_name,
                username=update.effective_user.username,
                is_premium=update.effective_user.is_premium or False,
                language_code=update.effective_user.language_code,
            )
        )
        if user.wallet:
            wallet_service = WalletService(db_session)
            if not user.wallet.hide_wallet:
                wallet_service.turn_visibility_off(user_id=user.id)
                # db_session.refresh(user)
                # await promote_user(context=context, user=user)
                return await connected_wallet_response(
                    db_session=db_session,
                    user=user,
                    context=context,
                    update=update,
                )
        else:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=update.effective_message.message_id,
                text="Wallet is not connected!",
                reply_markup=MAIN_BUTTON_REPLY_MARKUP,
            )
