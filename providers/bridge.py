import os

from starlette.requests import Request

from core.loader.loader import Loader
from providers.base import BaseProvider

PROVIDERS_PATH = os.path.join(os.path.dirname(__file__), "plugins")


class Bridge:
    def __init__(self):
        self.loader = Loader()
        self.providers = self.loader.load_plugins(
            PROVIDERS_PATH, BaseProvider, recursive=True
        )
        self.provider_list = {}

        # load provider instances
        for key in self.providers:
            Provider = self.providers[key]
            self.provider_list[key] = Provider()

    # link provider
    async def link_provider(
        self, provider_name: str, redirect_url: str, request: Request
    ):
        provider = self.provider_list[provider_name.lower()]
        if not provider:
            raise NotImplementedError

        return await provider.link_provider(redirect_url, request)

    # get access token
    async def get_access_token(self, provider_name: str, request: Request):
        provider = self.provider_list[provider_name.lower()]
        if not provider:
            raise NotImplementedError

        return await provider.get_access_token(request)

    # get access token from refresh_token
    async def get_access_token_from_refresh_token(
        self, provider_name: str, refresh_token: str
    ) -> str:
        provider = self.provider_list[provider_name.lower()]
        if not provider:
            raise NotImplementedError

        return await provider.get_access_token_from_refresh_token(refresh_token)

    # get session info
    async def get_session_info(self, provider_name: str, request: Request):
        provider = self.provider_list[provider_name.lower()]
        if not provider:
            raise NotImplementedError

        return await provider.get_session_info(request)

    # get profile
    def get_profile(self, provider_name: str, access_token: str, option: str):
        provider = self.provider_list[provider_name.lower()]
        if not provider:
            raise NotImplementedError

        return provider.get_profile(access_token, option)

    # get last message
    def get_last_message(self, provider_name: str, access_token: str, option: str):
        provider = self.provider_list[provider_name.lower()]
        if not provider:
            raise NotImplementedError

        return provider.get_last_message(access_token, option)

    def get_full_messages(
        self, provider_name: str, access_token: str, of_what: str, option: str
    ):
        provider = self.provider_list[provider_name.lower()]
        if not provider:
            raise NotImplementedError

        return provider.get_full_messages(access_token, of_what, option)

    # get messages
    def get_messages(
        self,
        provider_name: str,
        access_token: str,
        from_when: str,
        count: int,
        option: str,
    ):
        provider = self.provider_list[provider_name.lower()]
        if not provider:
            raise NotImplementedError

        return provider.get_messages(access_token, from_when, count, option)

    # reply to message
    def reply_to_message(
        self, provider_name: str, access_token: str, to: str, message: str, option: str
    ):
        provider = self.provider_list[provider_name.lower()]
        if not provider:
            raise NotImplementedError

        return provider.reply_to_message(access_token, to, message, option)

    # disconnect
    def disconnect(self, provider_name: str, request: Request):
        provider = self.provider_list[provider_name.lower()]
        if not provider:
            raise NotImplementedError

        return provider.disconnect(request)


bridge = Bridge()
