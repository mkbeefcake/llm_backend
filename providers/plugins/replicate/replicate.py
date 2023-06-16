import json

from fastapi.templating import Jinja2Templates
from starlette.requests import Request

import replica
from core.log import BackLog
from products.pinecone import PineconeService
from providers.base import BaseProvider
from services.service import ai_service

templates = Jinja2Templates(directory="templates/replicate")


def remove_brackets_and_braces(string):
    # Remove brackets [] & braces {}
    string = string.replace("[", "").replace("]", "")
    string = string.replace("{", "").replace("}", "")
    return string


class ReplicateProvider(BaseProvider, PineconeService):
    def __init__(self) -> None:
        super().__init__()
        self.num_messages = 2
        self.auth_json = {}
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

    def disconnect(self, request: Request):
        pass

    async def start_autobot(self, user_data: any):
        api = replica.select_api("replica")

        # try to get auth_json and rules from firestore db
        try:
            if "option" in user_data:
                self.auth_json = json.loads(user_data["option"])
                BackLog.info(instance=self, message=f"AUTH_JSON: {self.auth_json}")

            if "rules" in user_data:
                self.rules = json.loads(user_data["rules"])
                BackLog.info(instance=self, message=f"Rules: {self.rules}")

        except Exception as e:
            BackLog.exception(instance=self, message="Exception occurred")

        # authenticate
        authed = await self.authenticate(api)

        # get chat history per each user
        chats = await authed.get_chats()
        for chat in chats:
            user = await authed.get_user(chat["withUser"]["id"])
            BackLog.info(instance=self, message=f"Username: {user.name}")

            if not user.isPerformer:
                messages = await self.fetch_messages(user, authed)

                # build payload
                payload = self.build_payload(user_name=user.name, messages=messages)

                # response from ai model
                ai_response = ai_service.get_response(
                    service_name="replica_service",
                    option=payload,
                )
                BackLog.info(instance=self, message=f"Response from AI: {ai_response}")

                # get matched product based on conversation
                msg_str = ""
                for msg in messages:
                    msg_str += msg["role"] + ": " + msg["content"] + "\n"

                products = self.match_product(msg_str)
                BackLog.info(instance=self, message=f"Matched Product: {products}")

                # post ai message to user
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
