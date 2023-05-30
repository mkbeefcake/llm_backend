from abc import ABCMeta, abstractmethod
import sys
from starlette.requests import Request

from simple_classproperty import ClasspropertyMeta, classproperty


class BaseProviderBotMeta(ABCMeta, ClasspropertyMeta):
    pass


class BaseProviderBot(metaclass=BaseProviderBotMeta):
    @abstractmethod
    async def start(self, user_data: any):
        raise NotImplementedError
