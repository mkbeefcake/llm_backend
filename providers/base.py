import sys
from abc import ABCMeta, abstractmethod

from simple_classproperty import ClasspropertyMeta, classproperty
from starlette.requests import Request


class BaseProviderMeta(ABCMeta, ClasspropertyMeta):
    pass


class BaseProvider(metaclass=BaseProviderMeta):
    @abstractmethod
    async def link_provider(self, request: Request):
        raise NotImplementedError

    @abstractmethod
    async def get_access_token(self, request: Request) -> str:
        raise NotImplementedError

    @abstractmethod
    async def get_access_token_from_refresh_token(self, refresh_token: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def get_session_info(self, request: Request) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_profile(self, access_token: str, option: any):
        raise NotImplementedError

    @abstractmethod
    def get_last_message(self, access_token: str, option: any):
        raise NotImplementedError

    @abstractmethod
    def get_messages(self, access_token: str, from_when: str, count: int, option: any):
        raise NotImplementedError

    @abstractmethod
    def reply_to_message(self, access_token: str, to: str, message: str, option: any):
        raise NotImplementedError

    @abstractmethod
    def disconnect(self, request: Request):
        raise NotImplementedError

    @classproperty
    def plugin_name(cls) -> str:
        return cls.__name__  # type: ignore
