import sys
from providers.base import BaseProvider

class DummyProvider(BaseProvider):

    def get_access_token(self, email: str, password: str, option: any) -> str:
        print("[%s]: get_access_token: %s | %s" % (self.plugin_name, email, password), file=sys.stdout)

    def get_profile(self, access_token: str, option: any):
        print("[%s]: get_profile: %s " % (self.plugin_name, access_token), file=sys.stdout)
    
    def get_last_message(self, access_token: str, option: any):
        print("[%s]: get_last_message: %s " % (self.plugin_name, access_token), file=sys.stdout)

    def get_messages(self, access_token: str, from_when: str, option: any):
        print("[%s]: get_messages: %s %s" % (self.plugin_name, access_token, from_when), file=sys.stdout)
     
    def send_message(self, access_token: str, to: str, msg: str, option: any) -> None:
        print("[%s]: %s | %s : %s" % (self.plugin_name, access_token, to, msg), file=sys.stdout)

    def disconnect(self, access_token: str, option: any):
        print("[%s]: disconnect: %s" % (self.plugin_name, access_token), file=sys.stdout)

    pass