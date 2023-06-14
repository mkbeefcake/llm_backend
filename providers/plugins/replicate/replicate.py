import json
import random
import time
from urllib.parse import urlencode

import requests
import runpod
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

import replica
from products.pinecone import PineconeService
from providers.base import BaseProvider
from services.service import ai_service

runpod.api_key = "43G8Y6TUI5HBXEW4LFJRWOZE2R40GME2ZRIXR1H7"

templates = Jinja2Templates(directory="templates/replicate")


def remove_brackets_and_braces(string):
    # Remove brackets []
    string = string.replace("[", "").replace("]", "")
    # Remove braces {}
    string = string.replace("{", "").replace("}", "")
    return string


class ReplicateProvider(BaseProvider, PineconeService):
    def __init__(self) -> None:
        super().__init__()
        self.num_messages = 2
        self.auth_json = {
            "username": "default",
            "cookie": "csrf=N0uQpURU9336dbb53f166c906b74b178636e8e0a; c=230963499-93; cookiesAccepted=all; fp=d4b655c99f801e21d2576fe732d8a9ab; sess=rbo4f2f4c3bceldtjoaupfpt5o; auth_id=33685781; ref_src=; st=87d81fb3c07bb901ca3bb57628d29fb7064058179b331bfe41587fb2d27e32f1",
            "x_bc": "98178bf0df331fa7baee24df5fa6bf054b3eef77",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "email": "estefa.az.of@gmail.com",
            "password": "Teddy2010.",
            "hashed": False,
            "support_2fa": False,
            "active": True,
        }
        self.rules = {}

    def get_provider_info(self):
        return {
            "provider": ReplicateProvider.__name__.lower(),
            "short_name": "Replicate",
            "provider_description": "Replica Provider",
            "provider_icon_url": "",
        }

    async def link_provider(self, redirect_url: str, request: Request):
        return templates.TemplateResponse(
            "login.html", {"request": request, "redirect_url": redirect_url}
        )
        # response = RedirectResponse(
        #     url=redirect_url
        #     + "?provider=replicateprovider&"
        #     + urlencode(
        #         {
        #             "access_token": "fake_access_token",
        #             "refresh_token": "fake_refresh_token",
        #         }
        #     )
        # )
        # return response

    def disconnect(self, request: Request):
        pass

    async def get_bestseller_products(self):
        best_sellers = [{"product": "t-shirt", "price": 12.9, "unit": "usd"}]
        return best_sellers

    async def get_product_list(self):
        products = [
            {"product": "t-shirt", "price": 12.9, "unit": "usd"},
            {"product": "glasses", "price": 12.9, "unit": "usd"},
        ]
        return products

    async def suggest_products(self, conversation: str):
        # here use get_product_list, get_bestseller_products(), conversation
        # to decide products for user

        pass

    async def start_autobot(self, user_data: any):
        api = replica.select_api("replica")
        try:
            if "option" in user_data:
                self.auth_json = json.loads(user_data["option"])
                print("[Updated Auth_JSON]", self.auth_json)

            if "rules" in user_data:
                self.rules = json.loads(user_data["rules"])
                print("[Read Rules]", self.rules)

        except Exception as e:
            print("Error: ", str(e))

        authed = await self.authenticate(api)

        chats = await authed.get_chats()
        for chat in chats:
            user = await authed.get_user(chat["withUser"]["id"])
            print("[Username]: ", user.name)

            # get messages
            # authed

            if not user.isPerformer:
                messages = await self.fetch_messages(user, authed)

                # build payload
                payload = self.build_payload(user_name=user.name, messages=messages)

                # ai response
                ai_response = ai_service.get_response(
                    service_name="replica_service",
                    option=payload,
                )
                print("[aiRes]: ", ai_response)

                # Suggest product based on conversation
                msg_str = ""
                for msg in messages:
                    msg_str += msg["role"] + ": " + msg["content"] + "\n"

                print("[msg_str]: ", msg_str)

                products = self.suggest_products(msg_str)
                print("Products:", products)

                # await self.post_message(user, authed, ai_response["message"])

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
                if message["fromUser"]["id"] == user.id:
                    value = {"role": "user", "content": message["text"]}
                else:
                    value = {"role": "assistant", "content": message["text"]}

                messages.append(value)

            last_message_id = fetched_messages["list"][-1]["id"]

            if not fetched_messages["list"]:
                break

        return messages

    def build_payload(self, user_name: str, messages: any):
        prompt_template = ""
        if "prompt_template" in self.rules:
            prompt_template = self.rules["prompt_template"]

        character_name = ""
        if "character_name" in self.rules:
            character_name = self.rules["character_name"]

        context = ""
        if "context" in self.rules:
            context = self.rules["context"]

        data = {
            "input": {
                "input_text": remove_brackets_and_braces(
                    messages[0]["content"]
                ),  # this is the last message
                "prompt_template": prompt_template,
                "character_name": character_name,
                "your_name": user_name,
                "context": context,
                "history": messages,
            }
        }
        return data

    """ 
     async def get_products(self, user, authed, response):

        try:
            products = await authed.get_product_categories(user_id=user.id, text=response, price=0)
            return products
        except Exception:
            import traceback
            print(traceback.format_exc())
    """

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
