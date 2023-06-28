import asyncio
import json
import os

import requests
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

import replica
from core.utils.log import BackLog
from products.pinecone import pinecone_service
from providers.base import BaseProvider
from services.service import replica_service

templates = Jinja2Templates(directory="templates/replicate")
PRODUCT_REPLICA_ENDPOINT = os.getenv("PRODUCT_REPLICA_ENDPOINT")


def remove_brackets_and_braces(string):
    # Remove brackets [] & braces {}
    string = string.replace("[", "").replace("]", "")
    string = string.replace("{", "").replace("}", "")
    return string


def aggregate_labels(response_json):
    prediction = response_json["prediction"]
    values = [str(value) for value in prediction.keys()]
    result = ",".join(values)
    return result


async def label_content(type, url, k, id):
    endpoint = PRODUCT_REPLICA_ENDPOINT
    resource = requests.get(url)

    payload = {
        "k": k,
        "type": type,
    }
    response = requests.post(endpoint, files={"file": resource.content}, data=payload)
    response_json = response.json()
    return {"id": id, "label": aggregate_labels(response_json)}


class ReplicateProvider(BaseProvider):
    def __init__(self) -> None:
        super().__init__()
        self.num_messages = 2
        self.initialized = False
        self.api = None

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
        if self.api != None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.api.close_pools())
            loop.close()
        pass

    async def initialize(self, user_data: any):
        if self.initialized == True:
            return

        self.api = replica.select_api("replica")

        # try to get auth_json and rules from firestore db
        self.auth_json, self.rules = self.load_credentials_from_userdata(user_data)

        # authenticate
        self.authed = await self.authenticate(self.api, self.auth_json)
        BackLog.info(instance=self, message=f"Passed authenticate() function....")

        self.initialized = True
        pass

    async def start_autobot(self, user_data: any, option: any):
        await self.initialize(user_data=user_data)

        # Select relevant chats
        chats = await self.select_chats(self.authed, self.rules)

        for chat in chats:
            user = await self.authed.get_user(chat["withUser"]["id"])
            BackLog.info(instance=self, message=f"Username: {user.name}")

            try:
                if not user.isPerformer:
                    # fetch user's messages
                    messages = await self.fetch_messages(user, self.authed)

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
                            ],
                            option["namespace"],
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
                        rules=self.rules,
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
                        user, self.authed, ai_response, mediaFiles=product_id
                    )

            except Exception as e:
                BackLog.exception(instance=self, message=f"Exception occurred")

        # await api.close_pools()

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

    async def post_message(self, user, authed, response, price=0, mediaFiles=[]):
        try:
            await authed.send_message(
                user_id=user.id, text=response, price=price, mediaFiles=mediaFiles
            )
        except Exception:
            import traceback

            print(traceback.format_exc())

    async def get_purchased_products(self, user_data: any, option: any = None):
        chat_list = "NEW FANS (Regular price)✨"

        await self.initialize(user_data=user_data)

        print("Starting product scraping...")

        chat_lists = await self.authed.get_pinned_lists()
        print(chat_lists)

        # If the specified chat list exists, select chats from this list
        if chat_list in chat_lists:
            chats = await self.authed.get_chats(
                # We only want to get fans in the last 2 months, hence the 60 delta.
                identifier=f"&list_id={str(chat_lists[chat_list])}",
                delta=60,
            )
        else:
            # Filter them
            chats = await self.authed.get_chats(
                identifier=f"&list_id={chat_lists['Pinned']}"
            )

        user_id_list = [item["withUser"]["id"] for item in chats]
        all_users_info = {}

        for user_id in user_id_list:
            user_info = {}
            try:
                statistics = await self.authed.get_subscriber_info(user_id)
                user_info["statistics"] = statistics

                purchases = await self.authed.get_subscriber_gallery(user_id)
                purchased_items = []
                for item in purchases:
                    parsed_item = {
                        "message_id": item["message_id"],
                        "price": item["price"],
                        "medias": [item for item in item["media"]],
                        # "media_count": item["mediaCount"],
                        "created": item["createdAt"],
                        # "purchased": item["isOpened"],
                        "timestamp": item["createdAt"],
                    }
                    purchased_items.append(parsed_item)

                user_info["purchased"] = purchased_items

            except Exception as e:
                BackLog.exception(instance=self, message=f"{str(e)}")
                pass

            all_users_info[str(user_id)] = user_info

        # await api.close_pools()
        return all_users_info

    async def get_all_products(self, user_data: any, option: any = None):
        await self.initialize(user_data=user_data)

        categories = await self.authed.get_content_categories()

        full_content = []
        label_tasks = []  # This list will store the tasks for labeling the content

        print("Content List", len(full_content))
        for category in categories:
            offset = 0  # Create an offset variable
            hasMore = True  # Initialize hasMore as True

            while hasMore:  # While hasMore is true, continue fetching content
                content = await self.authed.get_content(str(offset), category["id"])
                print(category["id"], offset)

                if "hasMore" in content:
                    hasMore = content["hasMore"]

                    if len(content["list"]) > 0:
                        for item in content["list"]:
                            parsed_item = {
                                "category": category["name"],
                                "id": item["id"],
                                "type": item["type"],
                                "created": item["createdAt"],
                                "full": item["full"],
                            }

                            full_content.append(parsed_item)

                            # Add a task to label this content
                            try:
                                print(parsed_item["full"])
                                # print(parsed_item["full"], parsed_item["id"])
                                # base64_content = download_and_encode_content(parsed_item["full"], authed)

                                task = label_content(
                                    type=parsed_item["type"],
                                    url=parsed_item["full"],
                                    k=15,
                                    id=parsed_item["id"],
                                )
                                label_tasks.append(task)
                            except:
                                import traceback

                                print(traceback.print_exc())

                    offset += (
                        24  # Increase the offset by 24 for the next batch of content
                    )
                else:
                    break  # Break the loop if the content does not contain the "hasMore" key

        print(full_content)

        # Label all contents in parallel
        try:
            labels = await asyncio.gather(*label_tasks)
        except Exception as e:
            print(f"Error occurred: {e}")
            import traceback

            print(traceback.print_exc())

        for label in labels:
            print(label)
            # add_label_pinecone(label["label"], namespace=provider_id,  metadata)

        # await api.close_pools()

        BackLog.info(self, f"Products: {len(full_content)}")
        return {"products": labels}
