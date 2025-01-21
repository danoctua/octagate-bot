from core.settings import CoreSettings


class WalletIndexerSettings(CoreSettings):
    ton_api_key: str


wallet_indexer_settings = WalletIndexerSettings()
