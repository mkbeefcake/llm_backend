from core.task import task_manager
from db.cruds.provider import create_provider
from db.cruds.users import get_user_providers
from db.schemas.provider import ProviderSchema
from providers.bridge import bridge


class Provider:
    def __init__(self):
        pass

    # def create_provider(
    #     self, provider_name: str, provider_description: str, provider_icon_url: str
    # ):
    #     return create_provider(
    #         provider=ProviderSchema(
    #             provider_name, provider_description, provider_icon_url
    #         )
    #     )

    def get_my_providers(self, user):
        user_id = user["uid"]
        my_providers = get_user_providers(id=user_id)
        all_providers = self.get_all_providers()
        status_autobot = task_manager.status_my_auto_bot(user)
        return {
            "my_providers": my_providers,
            "providers": all_providers,
            "status_autobot": status_autobot,
        }

    def get_all_providers(self):
        return bridge.get_all_providers()

    # def get_provider(self, provider_name: str):
    #     return get_provider(provider_name)


provider = Provider()
