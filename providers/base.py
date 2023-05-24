from abc import ABCMeta
import sys

from simple_classproperty import ClasspropertyMeta, classproperty

class BaseProviderMeta(ABCMeta, ClasspropertyMeta):
    pass


class BaseProvider(metaclass=BaseProviderMeta):
    """
    You can use this class as a base class that can be loaded with the plugin loader.
    """
    def send_message(self, access_token: str, to: str, msg: str) -> None:
        """
        Print a message.
        All kwargs of regular 'print' are supported.
        @param msg: The message to print.
        @param file: The destination IO stream where the message is printed on (Default: stdout).
        """
        self.__print(access_token, to, msg)

    @classproperty
    def plugin_name(cls) -> str:
        """
        Get the name of the plugin.
        By default the class name is used.
        """
        return cls.__name__  # type: ignore

    def __print(self, access_token: str, to : str, msg: str) -> None:
        # insert the plugin name before the message
        print("[%s]: %s %s : %s" % (self.plugin_name, access_token, to, msg), file=sys.stdout)