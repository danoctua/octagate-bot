from core.settings import CoreSettings

DEFAULT_API_BASE_URL = "https://api.telegram.org/bot"


class BotUiSettings(CoreSettings):
    telegram_api_base_url: str = DEFAULT_API_BASE_URL

    webhook_prefix: str = "/webhook"
    webhook_url: str
    webhook_secret_key: str
    webhook_host: str = "0.0.0.0"
    webhook_port: int = 433

    ssl_cert_path: str
    ssl_key_path: str

    light_mode: bool
    enable_callback_replies: bool
    is_active: bool

    concurrent_updates: int = 256
    target_common_chat_id: int

    @property
    def full_webhook_url(self):
        return f"{bot_ui_settings.webhook_prefix}/{bot_ui_settings.webhook_url}/{bot_ui_settings.telegram_bot_token}"


bot_ui_settings = BotUiSettings()
