from pathlib import Path

POOL_TIMEOUT = 30
DEFAULT_CONNECT_TIMEOUT = 180
DEFAULT_EXPIRY_TIMEOUT_MINUTES = 30

DEFAULT_WALLET_BALANCE = 0

CUSTOM_TITLE_TEMPLATE = "Whale #{rank}"

DEFAULT_WALLET_TRACK_EXPIRATION = 60 * 60 * 24 * 365 * 10  # 10 years

# ------------------ Redis --------------------
UPDATED_WALLETS_SET_NAME = "updated_wallets"
CELERY_WALLET_FETCH_QUEUE_NAME = "wallet-fetch-queue"
CELERY_NOTICED_WALLETS_UPLOAD_QUEUE_NAME = "noticed-wallets-upload-queue"
CELERY_SYSTEM_QUEUE_NAME = "system-queue"

# ----------------- Paths ---------------------
PACKAGE_ROOT = Path(__file__).parent
PROJECT_ROOT = PACKAGE_ROOT.parent

# ---------------- Telethon --------------------
TELETHON_SESSION_PATH = PACKAGE_ROOT / "octagate.session"

# ---------------- Static files ----------------
STATIC_PATH = PACKAGE_ROOT / "static"
DEFAULTS_PATH = STATIC_PATH / "defaults"
# Jettons
JETTON_LOGO_SUB_PATH = "jettons"
JETTON_LOGO_PATH = STATIC_PATH / JETTON_LOGO_SUB_PATH
DEFAULT_JETTON_LOGO_PATH = DEFAULTS_PATH / "jetton.webp"
# NFTs
NFT_LOGO_SUB_PATH = "nfts"
NFT_LOGO_PATH = STATIC_PATH / NFT_LOGO_SUB_PATH
DEFAULT_NFT_LOGO_PATH = DEFAULTS_PATH / "nft.webp"
# Chats
CHAT_LOGO_SUB_PATH = "chats"
CHAT_LOGO_PATH = STATIC_PATH / CHAT_LOGO_SUB_PATH
DEFAULT_CHAT_LOGO_PATH = DEFAULTS_PATH / "chat.webp"
# Avatars
AVATAR_SUB_PATH = "avatars"
AVATAR_PATH = STATIC_PATH / AVATAR_SUB_PATH
DEFAULT_AVATAR_PATH = DEFAULTS_PATH / "avatar.webp"


MIGRATION_TO_ACCESS_TEXT = """Hey ANON\!

We\'ve migrated to a new tool that controls the access to the chat and here is the direct link for 8 Club:
https://t\.me/access\_app\_bot?startapp\=ch\_8\-club\.

More about the tool: https://t\.me/tools\_community/192942/192945\.

Even if you're already in the chat, please, make sure to **connect your wallet there to avoid being kicked out of the chat**\.

8 club members 🎱
"""
MIRATION_TO_ACCESS_BUTTON_URL = "https://t.me/access_app_bot?startapp=ch_8-club"
MIGRATION_TO_ACCESS_BUTTON_TEXT = "8 club [at] Access"
