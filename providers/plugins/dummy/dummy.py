import sys
from providers.base import BaseProvider
from starlette.requests import Request

class DummyProvider(BaseProvider):

    async def link_provider(self, request: Request):
        print("[%s]: link_provider: %s | %s" % (self.plugin_name, request), file=sys.stdout)

    async def get_access_token(self, request:Request) -> str:
        print("[%s]: get_access_token: %s | %s" % (self.plugin_name, request), file=sys.stdout)

    def get_profile(self, access_token: str, option: any):
        print("[%s]: get_profile: %s " % (self.plugin_name, access_token), file=sys.stdout)
    
    def get_last_message(self, access_token: str, option: any):
        print("[%s]: get_last_message: %s " % (self.plugin_name, access_token), file=sys.stdout)

    def get_messages(self, access_token: str, from_when: str, option: any):
        print("[%s]: get_messages: %s %s" % (self.plugin_name, access_token, from_when), file=sys.stdout)
     
    def disconnect(self, request:Request):
        print("[%s]: disconnect: %s" % (self.plugin_name), file=sys.stdout)

    pass