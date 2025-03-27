import logging
from pathlib import Path

from telethon import TelegramClient, events
from telethon.sessions import SQLiteSession

from community_manager.handlers.chat import (
    handle_join_request,
    handle_chat_action,
    handle_chat_participant_update,
)
from community_manager.settings import community_manager_settings
from core.services.supertelethon import TelethonService
from core.utils.events import ChatJoinRequestEventBuilder, ChatAdminChangeEventBuilder

logger = logging.getLogger(__name__)


def init_client():
    # Make session persistent for community manager
    session_path = Path(__file__).parent / "data"
    if not session_path.exists():
        session_path.mkdir(parents=True)

    session = SQLiteSession(str(session_path / "octagate.session"))
    client = TelegramClient(
        session,
        community_manager_settings.telegram_app_id,
        community_manager_settings.telegram_app_hash,
    )
    service = TelethonService(client=client)
    service.client.add_event_handler(handle_join_request, ChatJoinRequestEventBuilder())
    service.client.add_event_handler(handle_chat_action, events.ChatAction())
    service.client.add_event_handler(
        handle_chat_participant_update, ChatAdminChangeEventBuilder()
    )
    return service


def main():
    logger.info("Community Manager started.")
    telethon_service = init_client()
    telethon_service.start_sync()
    telethon_service.client.run_until_disconnected()


if __name__ == "__main__":
    main()
