import sys
from providers.base import BaseProvider

class GMailProvider(BaseProvider):

    def get_access_token(self, email: str, password: str, option: any) -> str:
        print("[%s]: get_access_token: %s | %s, %s" % (self.plugin_name, email, password, option), file=sys.stdout)

    def get_profile(self, access_token: str, option: any):
        print("[%s]: get_profile: %s, %s" % (self.plugin_name, access_token, option), file=sys.stdout)
    
    def get_last_message(self, access_token: str, option: any):
        print("[%s]: get_last_message: %s, %s" % (self.plugin_name, access_token, option), file=sys.stdout)

    def get_messages(self, access_token: str, from_when: str, option: any):
        print("[%s]: get_messages: %s %s, %s" % (self.plugin_name, access_token, from_when, option), file=sys.stdout)
     
    def send_message(self, access_token: str, to: str, msg: str, option: any) -> None:
        print("[%s]: %s | %s : %s, %s" % (self.plugin_name, access_token, to, msg, option), file=sys.stdout)

    def disconnect(self, access_token: str, option: any):
        print("[%s]: disconnect: %s, %s" % (self.plugin_name, access_token, option), file=sys.stdout)

    pass