import os


DEFAULT_API_BASE_URL = "https://api.telegram.org/bot"


class Config:
    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = os.getenv("REDIS_PORT")
    REDIS_QUEUE_NAME = os.getenv("REDIS_QUEUE_NAME")

    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_PORT = os.getenv("MYSQL_PORT")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_ROOT_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")

    MYSQL_CONNECTION_STRING = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_API_BASE_URL = os.getenv("TELEGRAM_API_BASE_URL", DEFAULT_API_BASE_URL)

    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    WEBHOOK_SECRET_KEY = os.getenv("WEBHOOK_SECRET_KEY")
    WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT") or 433)

    SSL_CERT_PATH = os.getenv("SSL_CERT_PATH")
    SSL_KEY_PATH = os.getenv("SSL_KEY_PATH")

    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

    ADMIN_IDS = [
        int(admin_id) for admin_id in os.getenv("ADMIN_IDS", "").split(",") if admin_id
    ]

    DEVELOPER_CHAT_ID = os.getenv("DEVELOPER_CHAT_ID")
    DEFAULT_LANGUAGE = "en"
    LANGUAGES = ["en"]

    LIGHT_MODE = bool(os.getenv("LIGHT_MODE") or 0)
    ENABLE_CALLBACK_REPLIES = bool(os.getenv("ENABLE_CALLBACK_REPLIES") or 0)
    IS_ACTIVE = bool(os.getenv("IS_ACTIVE") or 0)

    DEFAULT_QUEUE_BATCH_PROCESS_LIMIT = int(
        os.getenv("DEFAULT_QUEUE_BATCH_PROCESS_LIMIT") or 60
    )
    CONCURRENT_UPDATES = int(os.getenv("CONCURRENT_UPDATES") or 256)

    TON_API_KEY = os.getenv("TON_API_KEY")
    TARGET_JETTON_MASTER = os.getenv("TARGET_JETTON_MASTER")
    WHALE_RATING_THRESHOLD = int(os.getenv("WHALE_RATING_THRESHOLD") or 90)
    WHALE_BALANCE_THRESHOLD = int(os.getenv("WHALE_BALANCE_THRESHOLD") or 1_000_000)

    TC_MANIFEST_URL = os.getenv("TC_MANIFEST_URL", "https://raw.githubusercontent.com/XaBbl4/pytonconnect/main/pytonconnect-manifest.json")
    TARGET_COMMON_CHAT_ID = os.getenv("TARGET_COMMON_CHAT_ID")
