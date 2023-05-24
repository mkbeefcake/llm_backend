import os
from providers.loader.loader import Loader
from providers.base import BaseProvider

PROVIDERS_PATH = os.path.join(os.path.dirname(__file__), "plugins")

class Bridge:
    def __init__(self):
        self.loader = Loader()
        self.providers = self.loader.load_plugins(PROVIDERS_PATH, BaseProvider, recursive=True)
        self.provider_list = {}

        # load provider instances
        for key in self.providers:
            Provider = self.providers[key]
            self.provider_list[key] = Provider()

    # get access token
    def get_access_token(self, provider_name: str, email: str, password: str, option: str) -> str:
        provider = self.provider_list[provider_name.lower()]
        if not provider:
            raise NotImplementedError

        return provider.get_access_token(email, password, option)
    
    # get profile
    def get_profile(self, provider_name: str, access_token: str, option: str):
        provider = self.provider_list[provider_name.lower()]
        if not provider:
            raise NotImplementedError

        return provider.get_profile(access_token, option)
    
    # get last message
    def get_last_message(self, provider_name: str, access_token: str, option: str):
        provider = self.provider_list[provider_name.lower()]
        if not provider:
            raise NotImplementedError

        return provider.get_last_message(access_token, option)

    # get messages
    def get_messages(self, provider_name: str, access_token: str, from_when: str, option: str):
        provider = self.provider_list[provider_name.lower()]
        if not provider:
            raise NotImplementedError

        return provider.get_messages(access_token, from_when, option)

    # send message to provider
    def send_message(self, provider_name: str, access_token: str, to: str, msg: str, option: str):
        provider = self.provider_list[provider_name.lower()]
        if not provider:
            raise NotImplementedError

        return provider.send_message(access_token, to, msg, option)

    # disconnect
    def disconnect(self, provider_name:str, access_token: str, option: str):
        provider = self.provider_list[provider_name.lower()]
        if not provider:
            raise NotImplementedError

        return provider.disconnect(access_token, option)


bridge = Bridge()
