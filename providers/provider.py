import os
from providers.loader import Loader
from providers.base import BaseProvider

PROVIDERS_PATH = os.path.join(os.path.dirname(__file__), "plugins")
loader = Loader()
providers = loader.load_plugins(PROVIDERS_PATH, BaseProvider, recursive=True)
provider_list = {}

# load provider instances
for key in providers:
    Provider = providers[key]
    provider_list[key] = Provider()

def send_message(provider_name: str, access_token: str, to: str, msg: str):
    provider = provider_list[provider_name.lower()]

    if not provider:
        return None

    provider.send_message(access_token, to, msg)