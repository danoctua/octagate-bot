import asyncio

from pytonapi.utils import userfriendly_to_raw
from telethon import TelegramClient
from telethon.tl.types import ChannelParticipantsAdmins

from core.services.db import DBService
from core.services.user import UserService
from core.services.wallet import WalletService
from core.settings import Config


CHAT_NAME = "8 Club"


async def main():
    client = TelegramClient("anon", Config.TELEGRAM_APP_ID, Config.TELEGRAM_APP_HASH)
    await client.start()

    async for dialog in client.iter_dialogs():
        if dialog.name == CHAT_NAME:
            admins = await client.get_participants(
                dialog, filter=ChannelParticipantsAdmins
            )
            admins_by_id = {admin.id: admin for admin in admins}

            latest_processed_id = ...
            reached_latest_processed = False

            with DBService().db_session() as session:
                user_service = UserService(session)
                users = user_service.get_all_prefetched()
                wallet_service = WalletService(session)
                users_by_id = {}
                for user in users:
                    is_nft_holder = (
                        wallet_service.is_nft_holder(
                            owner_address=user.wallet.address,
                            collection_address=userfriendly_to_raw(
                                Config.TARGET_NFT_COLLECTION_ADDRESS
                            ),
                        )
                        if user.wallet
                        else False
                    )
                    user.is_nft_holder = is_nft_holder
                    users_by_id[user.telegram_id] = user

                participants = await client.get_participants(dialog)
                for idx, participant in enumerate(participants):
                    print(f"Processing participant {idx + 1}/{len(participants)}")
                    if not reached_latest_processed:
                        if participant.id == latest_processed_id:
                            print("Found latest processed ID")
                            reached_latest_processed = True
                        else:
                            continue
                    if participant.is_self:
                        print(f"PASS: User {participant.id} is self")
                        continue

                    elif participant.id in admins_by_id:
                        print(f"PASS: User {participant.id} is an admin")
                        continue

                    elif participant.bot:
                        print(f"PASS: User {participant.id} is a bot")
                        continue

                    user = users_by_id.get(participant.id)
                    is_eligible = user and user.is_eligible_club_member(
                        user.is_nft_holder
                    )
                    if not user or not is_eligible:
                        print(
                            f"KICK: User {participant.id} is not eligible to be in the club",
                            "no user found in the DB"
                            if not user
                            else f"{is_eligible=} {user.is_nft_holder=}",
                        )
                        await client.kick_participant(dialog, participant)
                        continue
                    else:
                        print(
                            f"PASS: User {participant.id} is eligible to be in the club"
                        )


if __name__ == "__main__":
    asyncio.run(main())
