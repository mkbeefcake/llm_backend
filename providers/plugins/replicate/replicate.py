import json

import replica
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from core.log import BackLog
from products.pinecone import pinecone_service
from providers.base import BaseProvider
from services.service import replica_service

templates = Jinja2Templates(directory="templates/replicate")


def remove_brackets_and_braces(string):
    # Remove brackets [] & braces {}
    string = string.replace("[", "").replace("]", "")
    string = string.replace("{", "").replace("}", "")
    return string


class ReplicateProvider(BaseProvider):
    def __init__(self) -> None:
        super().__init__()
        self.num_messages = 2

    def get_provider_info(self):
        return {
            "provider": ReplicateProvider.__name__.lower(),
            "short_name": "Replicate",
            "provider_description": "Replica Provider",
            "provider_icon_url": "/replicate.svg",
        }

    async def link_provider(self, redirect_url: str, request: Request):
        return templates.TemplateResponse(
            "login.html", {"request": request, "redirect_url": redirect_url}
        )

    def disconnect(self, request: Request):
        pass

    async def select_chats(self, authed, rules):
        """
        Select chats based on the 'chat_list' rule from the frontend.
        - If 'chat_list' rule does not exist, or if the specified chat list does not exist, all chats are selected.
        - Else, we select only the pinned list
        """
        if "chat_list" in rules:
            # Get chat lists
            chat_lists = await authed.get_pinned_lists()
            BackLog.info(instance=self, message=f"Chat Lists: {chat_lists}")

            # If the specified chat list exists, select chats from this list
            if rules["chat_list"] in chat_lists:
                BackLog.info(instance=self, message=f"Chat Lists: {chat_lists}")
                return await authed.get_chats(
                    identifier=f"&list_id={str(chat_lists[rules['chat_list']])}"
                )

        # If 'chat_list' rule does not exist, or if the specified chat list does not exist, select all chats
        BackLog.info(instance=self, message=f"Fetching all chats")
        return await authed.get_chats()

    async def start_autobot(self, user_data: any):
        api = replica.select_api("replica")

        # try to get auth_json and rules from firestore db
        auth_json, rules = self.load_credentials_from_userdata(user_data)

        # authenticate
        authed = await self.authenticate(api, auth_json)
        BackLog.info(instance=self, message=f"Passed authenticate() function....")

        # Select relevant chats
        chats = await self.select_chats(authed, rules)

        for chat in chats:
            user = await authed.get_user(chat["withUser"]["id"])
            BackLog.info(instance=self, message=f"Username: {user.name}")

            try:
                if not user.isPerformer:
                    # fetch user's messages
                    messages = await self.fetch_messages(user, authed)

                    # suggest product from ai
                    payload_product = self.build_payload_for_Product(messages=messages)
                    suggested_products = replica_service.suggest_product(
                        messages=messages, option=payload_product
                    )
                    BackLog.info(
                        instance=self,
                        message=f"Suggested Product from AI: {suggested_products}",
                    )

                    # if a product is suggested, we match it in the db and retrieve the product id
                    if (
                        suggested_products["search_product_processed"]["product_intent"]
                        == True
                    ):
                        product_id = pinecone_service.match_product(
                            suggested_products["search_product_processed"][
                                "product_description"
                            ]
                        )
                        product_message = f'The user might be interested by {suggested_products["search_product_processed"][ "product_description"]}'
                        BackLog.info(
                            instance=self, message=f"Matched Product: {product_id}"
                        )
                    else:
                        product_id = []
                        product_message = ""

                    # build payload & get ai response
                    payload_ai = self.build_payload_for_AI(
                        user_name=user.name,
                        messages=messages,
                        rules=rules,
                        product_message=product_message,
                    )

                    ai_response = replica_service.get_response(
                        message=messages[0]["content"],
                        option=payload_ai,
                    )
                    BackLog.info(
                        instance=self, message=f"Response from AI: {ai_response}"
                    )

                    # post ai message to user
                    await self.post_message(
                        user, authed, ai_response, mediaFiles=product_id
                    )

            except Exception as e:
                BackLog.exception(instance=self, message=f"Exception occurred")

        await api.close_pools()

    def load_credentials_from_userdata(self, user_data):
        auth_json = {}
        rules = {}

        try:
            if "option" in user_data:
                auth_json = json.loads(user_data["option"])
                BackLog.info(instance=self, message=f"AUTH_JSON: {auth_json}")

            if "rules" in user_data:
                rules = json.loads(user_data["rules"])
                BackLog.info(instance=self, message=f"Rules: {rules}")

        except Exception as e:
            BackLog.exception(instance=self, message="Exception occurred")

        return auth_json, rules

    async def authenticate(self, api: replica.api_types, auth_json):
        BackLog.info(
            instance=self,
            message=f"Type: {type(auth_json)}, Creds: {auth_json}",
        )
        auth = api.add_auth(auth_json)
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

    def build_payload_for_Product(self, messages: any):
        payload = {"input": {"search_prod_input": {"history": messages}}}
        return payload

    def build_payload_for_AI(
        self, user_name: str, messages: any, rules, product_message=""
    ):
        prompt_template = ""
        if "prompt_template" in rules:
            prompt_template = rules["prompt_template"]

        character_name = ""
        if "character_name" in rules:
            character_name = rules["character_name"]

        context = ""
        if "context" in rules:
            context = rules["context"] + product_message

        payload = {
            "input": {
                "conversation_input": {
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
        }
        return payload

    """ 
     async def get_products(self, user, authed, response):

        try:
            products = await authed.get_product_categories(user_id=user.id, text=response, price=0)
            return products
        except Exception:
            import traceback
            print(traceback.format_exc())
    """

    async def post_message(self, user, authed, response, price=0, mediaFiles=[]):
        # Get user input
        # user_input = input("Please input the message you want to send: ")

        # If user input is not empty, use it instead of the response
        # if user_input:
        #     response = user_input

        try:
            await authed.send_message(
                user_id=user.id, text=response, price=price, mediaFiles=mediaFiles
            )
        except Exception:
            import traceback

            print(traceback.format_exc())
