from abc import ABCMeta, abstractmethod
import sys

from simple_classproperty import ClasspropertyMeta, classproperty

class BaseProviderMeta(ABCMeta, ClasspropertyMeta):
    pass


class BaseProvider(metaclass=BaseProviderMeta):

    @abstractmethod
    def get_access_token(self, email: str, password: str, option: any) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_profile(self, access_token: str, option: any):
        raise NotImplementedError
    
    @abstractmethod    
    def get_last_message(self, access_token: str, option: any):
        raise NotImplementedError

    @abstractmethod
    def get_messages(self, access_token: str, from_when: str, option: any):
        raise NotImplementedError
     
    @abstractmethod
    def disconnect(self, access_token: str, option: any):
        raise NotImplementedError

    @classproperty
    def plugin_name(cls) -> str:
        return cls.__name__  # type: ignore

