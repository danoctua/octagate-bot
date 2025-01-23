from core.db import Base

from core.models.blockchain import Jetton, NFTCollection, NftItem  # noqa
from core.models.chat import (  # noqa
    TelegramChat,
    TelegramChatJetton,
    TelegramChatNFTCollection,
    TelegramChatUser,
)
from core.models.user import User  # noqa
from core.models.wallet import UserWallet, JettonWallet  # noqa


# To prevent imports from this module
# Only Base should be imported from this module to import models by migrator
__all__ = ["Base"]
