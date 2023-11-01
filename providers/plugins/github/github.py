import sys

from starlette.requests import Request

from providers.nango import NangoProvider


class GithubProvider(NangoProvider):
    def get_provider_info(self):
        return {
            "provider": GithubProvider.__name__.lower(),
            "short_name": "Github",
            "provider_description": "Github Provider",
            "provider_icon_url": "/github.svg",
            "provider_type": "nango",
            "provider_unique_key": "demo-github-integration"
        }

    async def link_provider(self, redirect_url: str, request: Request):
        print(f'GitHub: link_provider: {redirect_url}')
        return await super().link_provider(redirect_url, request)

    async def get_access_token(self, request: Request) -> str:
        return super().get_access_token(request)

    async def get_access_token_from_refresh_token(self, refresh_token: str) -> str:
        return super().get_access_token_from_refresh_token(refresh_token)

    def get_last_message(self, access_token: str, option: any):
        return super().get_last_message(access_token, option)

    def get_full_messages(self, access_token: str, of_what: str, option: any):
        return super().get_full_messages(access_token, of_what, option)

    def get_messages(self, access_token: str, from_when: str, count: int, option: any):
        return super().get_messages(access_token, from_when, count, option)

    def reply_to_message(self, access_token: str, to: str, message: str, option: any):
        return super().reply_to_message(access_token, to, message, option)

    async def disconnect(self, request: Request):
        return super().disconnect(request)

    async def start_autobot(self, user_data: any, option: any):
        return super().start_autobot(user_data, option)

    pass
