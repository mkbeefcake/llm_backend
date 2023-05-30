import sys
from abc import ABCMeta, abstractmethod

from simple_classproperty import ClasspropertyMeta, classproperty
from starlette.requests import Request


class BaseProviderBotMeta(ABCMeta, ClasspropertyMeta):
    pass


class BaseProviderBot(metaclass=BaseProviderBotMeta):
    @abstractmethod
    async def start(self, user_data: any):
        raise NotImplementedError
