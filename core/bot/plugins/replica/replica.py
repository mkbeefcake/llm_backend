
from google.auth.exceptions import RefreshError
import replica
from core.bot.base import BaseProviderBot
from core.timestamp import get_current_timestamp
from providers.bridge import bridge
from services.service import ai_service

PROVIDER_NAME = "ReplicaProvider"
MAX_MAIL_COUNT = 10


class ReplicaProviderBot(BaseProviderBot):
    def __init__(self):
            self.sync_time = -1
            self.access_token = None
            self.refresh_token = None


    async def start(self, user_data: any):):
        api = replica.select_api("replica")
        authed = await self.authenticate(api)

        chats = await authed.get_chats()
        for chat in chats:
            user = await authed.get_user(chat["withUser"]["id"])
            print(user.name)
            if not user.isPerformer:
                messages = await self.fetch_messages(user, authed)
                print(messages)
                llm_response = await self.call_llm_server(messages, user_name=user.name)
                await self.post_message(user, authed, llm_response)

        await api.close_pools()


