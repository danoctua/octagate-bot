import asyncio
import datetime
import logging
from io import BytesIO

from pytonapi.utils import userfriendly_to_raw
import qrcode
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from core.constants import DEFAULT_CONNECT_TIMEOUT
from core.renderers import connected_wallet_welcome_renderer, MAIN_BUTTON_REPLY_MARKUP
from core.services.db import DBService
from core.services.storage import get_connector
from core.services.user import UserService
from core.services.wallet import WalletService, UserWalletExistError
from core.settings import Config
from core.utils.authorization import (
    demote_user,
    promote_user,
    get_telegram_chat_member,
    is_telegram_chat_admin,
)
from core.utils.bot import delete_message

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
            user = user_service.get_or_create(telegram_user=update.effective_user)
            if user.wallet:
                wallet_service = WalletService(db_session)
                is_nft_holder = wallet_service.is_nft_holder(
                    owner_address=user.wallet.address,
                    collection_address=userfriendly_to_raw(
                        Config.TARGET_NFT_COLLECTION_ADDRESS
                    ),
                )
                await connected_wallet_welcome_renderer(
                    update, context, user, is_nft_holder
                )
                await delete_message(
                    context=context,
                    chat_id=update.effective_chat.id,
                    message_id=update.effective_message.message_id,
                )
                return
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
                        telegram_user=update.effective_user
                    )
                    wallet_service = WalletService(db_session)
                    try:
                        wallet_service.connect_user_wallet(
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

                    wallet_service.link_user_jetton_wallet(
                        wallet_address=connector.account.address
                    )
                    db_session.commit()

                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="Wallet connected successfully!",
                    )
                    await delete_message(
                        context=context,
                        chat_id=update.effective_chat.id,
                        message_id=message.message_id,
                    )
                    await promote_user(context=context, user=user)
                    connector.pause_connection()
                    # This is required to refresh user with all related data
                    user = user_service.get_or_create(
                        telegram_user=update.effective_user
                    )
                    is_nft_holder = wallet_service.is_nft_holder(
                        owner_address=user.wallet.address,
                        collection_address=userfriendly_to_raw(
                            Config.TARGET_NFT_COLLECTION_ADDRESS
                        ),
                    )
                    return await connected_wallet_welcome_renderer(
                        update,
                        context,
                        user,
                        is_nft_holder,
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
    is_connected = connector.connected
    if not is_connected:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Wallet is not connected!",
            reply_markup=MAIN_BUTTON_REPLY_MARKUP,
        )
        await delete_message(
            context, update.effective_chat.id, update.effective_message.message_id
        )
        return

    await demote_user(context=context, telegram_id=update.effective_user.id)
    await connector.disconnect()
    chat_member = await get_telegram_chat_member(context, update.effective_user.id)
    if chat_member is not None:
        if is_telegram_chat_admin(chat_member):
            logger.warning(
                "Skipping banning user `%d` from group because user is non-whale admin",
                update.effective_user.id,
            )
        else:
            logger.info(
                "Banning user `%d` from group because of disconnecting wallet",
                update.effective_user.id,
            )
            await context.bot.ban_chat_member(
                chat_id=Config.TARGET_COMMON_CHAT_ID,
                user_id=update.effective_user.id,
                until_date=60,  # ban for a minute so that user can join again in a minute
            )
    else:
        logger.info(
            "Failed to ban user `%d` from group because user is not a chat member",
            update.effective_user.id,
        )
    with DBService().db_session() as db_session:
        user_service = UserService(db_session)
        user = user_service.get_or_create(telegram_user=update.effective_user)
        wallet_service = WalletService(db_session)
        wallet_service.disconnect_user_wallet(user_id=user.id)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Wallet disconnected successfully!",
            reply_markup=MAIN_BUTTON_REPLY_MARKUP,
        )
        await delete_message(
            context, update.effective_chat.id, update.effective_message.message_id
        )
