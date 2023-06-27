import sys
from abc import ABCMeta, abstractmethod

from simple_classproperty import ClasspropertyMeta, classproperty
from starlette.requests import Request


class BaseProviderMeta(ABCMeta, ClasspropertyMeta):
    pass


class BaseProvider(metaclass=BaseProviderMeta):
    def get_provider_info(self):
        return {
            "provider": BaseProvider.__name__.lower(),
            "provider_description": "Base Provider",
            "provider_icon_url": "",
        }

    async def link_provider(self, redirect_url: str, request: Request):
        raise NotImplementedError

    async def get_access_token(self, request: Request) -> str:
        raise NotImplementedError

    async def get_access_token_from_refresh_token(self, refresh_token: str) -> str:
        raise NotImplementedError

    async def get_session_info(self, request: Request) -> str:
        raise NotImplementedError

    def get_profile(self, access_token: str, option: any):
        raise NotImplementedError

    def get_last_message(self, access_token: str, option: any):
        raise NotImplementedError

    def get_full_messages(self, access_token: str, of_what: str, option: any):
        raise NotImplementedError

    def get_messages(self, access_token: str, from_when: str, count: int, option: any):
        raise NotImplementedError

    def reply_to_message(self, access_token: str, to: str, message: str, option: any):
        raise NotImplementedError

    def disconnect(self, request: Request):
        raise NotImplementedError

    async def start_autobot(self, user_data: any):
        raise NotImplementedError

    async def get_purchased_products(self, user_data: any):
        raise NotImplementedError

    async def get_all_products(self, user_data: any):
        raise NotImplementedError

    @classproperty
    def plugin_name(cls) -> str:
        return cls.__name__  # type: ignore
