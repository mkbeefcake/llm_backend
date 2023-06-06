import asyncio
# import replica
import json
import random
import time

import requests
import runpod
from starlette.requests import Request

from providers.base import BaseProvider

runpod.api_key = "43G8Y6TUI5HBXEW4LFJRWOZE2R40GME2ZRIXR1H7"


def remove_brackets_and_braces(string):
    # Remove brackets []
    string = string.replace("[", "").replace("]", "")
    # Remove braces {}
    string = string.replace("{", "").replace("}", "")
    return string


class ReplicateProvider(BaseProvider):
    async def link_provider(self, redirect_url: str, request: Request):
        pass

    async def get_access_token(self, request: Request) -> str:
        pass

    async def get_access_token_from_refresh_token(self, refresh_token: str) -> str:
        pass

    async def get_session_info(self, request: Request) -> str:
        pass

    def get_profile(self, access_token: str, option: any):
        pass

    def get_last_message(self, access_token: str, option: any):
        pass

    def get_full_messages(self, access_token: str, of_what: str, option: any):
        pass

    def get_messages(self, access_token: str, from_when: str, count: int, option: any):
        pass

    def reply_to_message(self, access_token: str, to: str, message: str, option: any):
        pass

    def disconnect(self, request: Request):
        pass

    async def start_autobot(self, user_data: any):
        pass

    # async def _authenticate(self, api: replica.api_types):
    #     self.auth_json = {
    #         "username": "default",
    #         "cookie": "csrf=N0uQpURU9336dbb53f166c906b74b178636e8e0a; c=230963499-93; cookiesAccepted=all; sess=1qnp1476pbhvu3t137qbtcbqc9; auth_id=33685781; fp=740b75a6cbca25584887af6fb7cd1d09; ref_src=; st=e33ddd20bb1f6b022067240adb412d0747206a0f49f92e2844a91bb81923dea0",
    #         "x_bc": "98178bf0df331fa7baee24df5fa6bf054b3eef77",
    #         "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    #         "email": "estefa.az.of@gmail.com",
    #         "password": "Teddy2010.",
    #         "hashed": False,
    #         "support_2fa": False,
    #         "active": True
    #     }
    #     auth = api.add_auth(self.auth_json)
    #     return await auth.login()

    # async def _get_last_message(self, user, authed):
    #     last_message = await user.get_message()
    #     return last_message

    # async def _get_messages(self, user, authed, num_messages):
    #     messages = []
    #     last_message_id = None

    #     while len(messages) < self.num_messages:
    #         fetched_messages = await user.get_message(last_message=last_message_id)
    #         for message in fetched_messages["list"]:
    #             #messages.append([message["fromUser"]["id"], message["text"]])
    #             messages.append(message["text"])

    #         last_message_id = fetched_messages["list"][-1]["id"]

    #         if not fetched_messages["list"]:
    #             break

    #     return messages

    # async def _reply_to_message(self, user, authed, response):
    #     # Get user input
    #     user_input = input("Please input the message you want to send: ")

    #     # If user input is not empty, use it instead of the response
    #     if user_input:
    #         response = user_input

    #     try:
    #         await authed.send_message(user_id=user.id, text=response, price=0)
    #     except Exception:
    #         import traceback
    #         print(traceback.format_exc())
