from typing import TypedDict

from telegram import InlineKeyboardMarkup, InputMediaAnimation


class TelegramSendMessageWithKeyboardDTO(TypedDict):
    chat_id: int
    text: str
    reply_markup: InlineKeyboardMarkup


class TelegramEditMessageWithKeyboardDTO(TelegramSendMessageWithKeyboardDTO):
    message_id: int


class TelegramEditMediaWithKeyboardDTO(TypedDict):
    chat_id: int
    message_id: int
    media: InputMediaAnimation
    reply_markup: InlineKeyboardMarkup
