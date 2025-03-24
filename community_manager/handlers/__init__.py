from telethon import events

from core.services.supertelethon import TelethonService
from core.utils.events import ChatJoinRequestEvent
from community_manager.handlers.chat import handle_chat_action, handle_join_request


def init_client():
    service = TelethonService()
    service.client.add_event_handler(handle_join_request, ChatJoinRequestEvent())
    service.client.add_event_handler(handle_chat_action, events.ChatAction())
    return service


telethon_service = init_client()
octagate_bot_client = telethon_service.client
