from core.settings import CoreSettings


class CommunityManagerSettings(CoreSettings):
    ton_api_key: str

    worker_concurrency: int = 1


community_manager_settings = CommunityManagerSettings()
