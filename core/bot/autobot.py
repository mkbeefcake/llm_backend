import os

from core.loader.loader import Loader
from db.cruds.users import get_user_data
from providers.bridge import bridge

BOTS_PATH = os.path.join(os.path.dirname(__file__), "plugins")


class AutoBot:
    def __init__(self):
        pass

    async def start(self, user: any, provider_name: str, identifier_name: str):
        user_id = user["uid"]
        user_data = get_user_data(user_id)

        if provider_name in user_data and identifier_name in user_data[provider_name]:
            await bridge.start_autobot(
                provider_name,
                identifier_name,
                user_data[provider_name][identifier_name],
            )
        else:
            await bridge.start_autobot(provider_name, identifier_name, None)
        pass


autobot = AutoBot()
