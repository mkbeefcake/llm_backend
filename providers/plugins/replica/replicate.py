import asyncio
import json
import random
import time
from urllib.parse import urlencode

import requests
import runpod
from fastapi.responses import RedirectResponse
from starlette.requests import Request

import replica
from providers.base import BaseProvider

runpod.api_key = "43G8Y6TUI5HBXEW4LFJRWOZE2R40GME2ZRIXR1H7"


def remove_brackets_and_braces(string):
    # Remove brackets []
    string = string.replace("[", "").replace("]", "")
    # Remove braces {}
    string = string.replace("{", "").replace("}", "")
    return string


class ReplicateProvider(BaseProvider):
    def __init__(self) -> None:
        super().__init__()
        self.num_messages = 2
        self.auth_json = {
            "username": "default",
            "cookie": "csrf=N0uQpURU9336dbb53f166c906b74b178636e8e0a; c=230963499-93; cookiesAccepted=all; fp=d4b655c99f801e21d2576fe732d8a9ab; sess=ctklgm65nsr53p6m0na6fpuhuc; auth_id=33685781; ref_src=; st=d044383d5f613ea06d757c847a3c696b5aa6ef7a2b0f4620aab529d17fc9bf49",
            "x_bc": "98178bf0df331fa7baee24df5fa6bf054b3eef77",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "email": "estefa.az.of@gmail.com",
            "password": "Teddy2010.",
            "hashed": False,
            "support_2fa": False,
            "active": True,
        }

    def get_provider_info(self):
        return {
            "provider": ReplicateProvider.__name__.lower(),
            "provider_description": "Replica Provider",
            "provider_icon_url": "",
        }

    async def link_provider(self, redirect_url: str, request: Request):
        response = RedirectResponse(
            url=redirect_url
            + "?provider=replicateprovider&"
            + urlencode(
                {
                    "access_token": "fake_access_token",
                    "refresh_token": "fake_refresh_token",
                }
            )
        )
        return response

    def disconnect(self, request: Request):
        pass

    async def start_autobot(self, user_data: any):
        api = replica.select_api("replica")
        authed = await self.authenticate(api)

        chats = await authed.get_chats()
        for chat in chats:
            user = await authed.get_user(chat["withUser"]["id"])
            print(user.name)
            if not user.isPerformer:
                messages = await self.fetch_messages(user, authed)
                print(messages)
                llm_response = await self.call_llm_server(messages, user_name=user.name)
                await self.post_message(user, authed, llm_response)

        await api.close_pools()

    async def authenticate(self, api: replica.api_types):
        auth = api.add_auth(self.auth_json)
        return await auth.login()

    async def fetch_messages(self, user, authed):
        messages = []
        last_message_id = None

        while len(messages) < self.num_messages:
            fetched_messages = await user.get_message(last_message=last_message_id)
            for message in fetched_messages["list"]:
                # messages.append([message["fromUser"]["id"], message["text"]])
                messages.append(message["text"])

            last_message_id = fetched_messages["list"][-1]["id"]

            if not fetched_messages["list"]:
                break

        return messages

    async def call_llm_server(self, messages, user_name):
        url = "https://api.runpod.ai/v2/mugq8uc1sdkbyy/run"
        headers = {
            "Content-Type": "text/plain",
            "Authorization": "Bearer 43G8Y6TUI5HBXEW4LFJRWOZE2R40GME2ZRIXR1H7",
            "Cookie": "__cflb=02DiuEDmJ1gNRaog7BueRQnZrHB1BtXddnpJGyoZEckYk",
        }

        data = {
            "input": {
                "input_text": remove_brackets_and_braces(messages[0]),
                "user_id": random.randint(10, 900),
                "prompt_template": "(full name - Estefania) is a 23 year old Colombian female. She is nice and caring. ",
                "character_name": "Estefania",
                "your_name": user_name,
            }
        }

        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()
        id_1, status_1 = response_data["id"], response_data["status"]
        print(f"ID: {id_1}, Status: {status_1}")

        time.sleep(10)

        status_url = f"https://api.runpod.ai/v2/mugq8uc1sdkbyy/status/{id_1}"
        status_response = requests.get(status_url, headers=headers)
        status_data = status_response.json()
        output = status_data
        print(output)

        return output

    async def post_message(self, user, authed, response):
        # Get user input
        # user_input = input("Please input the message you want to send: ")

        # If user input is not empty, use it instead of the response
        # if user_input:
        #     response = user_input

        try:
            await authed.send_message(user_id=user.id, text=response, price=0)
        except Exception:
            import traceback

            print(traceback.format_exc())
