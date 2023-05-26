from abc import ABCMeta, abstractmethod
import sys
from starlette.requests import Request

from simple_classproperty import ClasspropertyMeta, classproperty

class BaseProviderMeta(ABCMeta, ClasspropertyMeta):
    pass


class BaseProvider(metaclass=BaseProviderMeta):

    @abstractmethod
    async def link_provider(self, request: Request):
        raise NotImplementedError

    @abstractmethod
    async def get_access_token(self, request:Request) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_profile(self, access_token: str, option: any):
        raise NotImplementedError
    
    @abstractmethod    
    def get_last_message(self, access_token: str, option: any):
        raise NotImplementedError

    @abstractmethod
    def get_messages(self, access_token: str, from_what: str, count: int, option: any):
        raise NotImplementedError
     
    @abstractmethod
    def disconnect(self, request: Request):
        raise NotImplementedError

    @classproperty
    def plugin_name(cls) -> str:
        return cls.__name__  # type: ignore

