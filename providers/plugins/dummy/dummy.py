import sys
from providers.base import BaseProvider

class DummyProvider(BaseProvider):

    def send_message(self, access_token: str, to: str, msg: str) -> None:
        """
        Print a message.
        All kwargs of regular 'print' are supported.
        @param msg: The message to print.
        @param file: The destination IO stream where the message is printed on (Default: stdout).
        """
        print("[%s]: %s | %s : %s" % (self.plugin_name, access_token, to, msg), file=sys.stdout)

    pass