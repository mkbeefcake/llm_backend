import asyncio
import json
import os

import replica
import requests
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

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


async def label_content(type, url, k, id, item):
    endpoint = PRODUCT_REPLICA_ENDPOINT
    resource = requests.get(url)

    payload = {
        "k": k,
        "type": type,
    }
    response = requests.post(endpoint, files={"file": resource.content}, data=payload)
    response_json = response.json()
    return {
        "id": id,
        "label": aggregate_labels(response_json),
        "category": item["category"],
        "createdAt": item["created"],
        "type": item["type"],
        "full": item["full"],
    }


class ReplicateProvider(BaseProvider):
    def __init__(self) -> None:
        super().__init__()
        self.num_messages = 2
        self.initialized = False
        self.api = None
        self.delta = 0
        self.product_limit_per_category = 0

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
        # if self.initialized == True:
        #     return

        self.api = replica.select_api("replica")

        # try to get auth_json and rules from firestore db
        self.auth_json, self.rules = self.load_credentials_from_userdata(user_data)

        # authenticate
        self.authed = await self.authenticate(self.api, self.auth_json)
        BackLog.info(
            instance=self,
            message=f"{self.identifier_name}: Passed authenticate() function....",
        )

        self.initialized = True
        pass

    async def start_autobot(self, user_data: any, option: any):
        await self.initialize(user_data=user_data)

        # Select relevant chats
        chats = await self.select_chats(self.authed, self.rules)

        for chat in chats:
            user = await self.authed.get_user(chat["withUser"]["id"])
            BackLog.info(
                instance=self, message=f"{self.identifier_name}: Username: {user.name}"
            )

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
                        message=f"{self.identifier_name}: Suggested Product from AI: {suggested_products}",
                    )

                    # if a product is suggested, we match it in the db and retrieve the product id
                    if (
                        suggested_products["search_product_processed"]["product_intent"]
                        == True
                    ):
                        product_matches = pinecone_service.match_product(
                            suggested_products["search_product_processed"][
                                "product_description"
                            ],
                            option,
                        )
                        BackLog.info(
                            instance=self,
                            message=f"{self.identifier_name}: Product matches: {product_matches}",
                        )

                        # Assess if product is in user history. Take the first product not in history.
                        product_history = self.get_purchase_history(
                            chat["withUser"]["id"], option["purchased"]
                        )
                        BackLog.info(
                            instance=self,
                            message=f"{self.identifier_name}: Purchased history: {product_history}",
                        )
                        product_id = next(
                            (
                                element
                                for element in product_matches
                                if element not in product_history
                            ),
                            None,
                        )
                        BackLog.info(
                            instance=self,
                            message=f"{self.identifier_name}: Matched Product: {product_id}",
                        )

                        # fetch user info
                        user_info = self.fetch_user_info(
                            chat["withUser"]["id"], option["purchased"]
                        )
                        BackLog.info(
                            instance=self,
                            message=f"{self.identifier_name}: User Purchased: {user_info}",
                        )

                        # fetch product info
                        product_info = self.fetch_product_info(
                            product_id, option["products"]
                        )
                        BackLog.info(
                            instance=self,
                            message=f"{self.identifier_name}: User Product: {product_info}",
                        )

                        # price product
                        product_price = self.predict_product_price(
                            user_info, product_info
                        )
                        BackLog.info(
                            instance=self,
                            message=f"{self.identifier_name}: Product Priced at: {product_price}",
                        )

                        # Adjust prompt for AI to sell product
                        product_message = "\n You will now act as a sales agent too who will give detail about product to the user too. " \
                                          "The product details are: {product_description} And Convice {human_prefix} to buy it. " \
                                          "You Must convince user to buy {product_description}, priced at {product_price} \n"

                        product_message.format(product_description=suggested_products[
                            "search_product_processed"]["product_description"],
                                               product_price=product_price,
                                               human_prefix=user.name)

                    else:
                        product_id = []
                        product_message = ""
                        product_price = 0

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
                        instance=self,
                        message=f"{self.identifier_name}: Response from AI: {ai_response}",
                    )

                    # post ai message to user
                    await self.post_message(
                         user, self.authed, ai_response, mediaFiles=product_id, price=product_price
                     )

            except Exception as e:
                BackLog.exception(
                    instance=self,
                    message=f"{self.identifier_name}: Exception occurred...",
                )

        # await api.close_pools()

    async def select_chats(self, authed, rules):
        """
        Select chats based on the 'chat_list' rule from the frontend.
        - If 'chat_list' rule does not exist, or if the specified chat list does not exist, all chats are selected.
        - Else, we select only the pinned list

        Available rules :
        - unread

        """
        # BackLog.info(instance=self, message=f"{self.identifier_name}: Rules: {rules}")
        if "chat_list" in rules:
            if rules["chat_list"] == "unread":
                BackLog.info(
                    instance=self,
                    message=f"{self.identifier_name}: Fetching unread chats, delta = {self.delta}",
                )
                if self.delta > 0:
                    return await authed.get_chats(
                        identifier="&filter=unread", delta=self.delta
                    )
                else:
                    return await authed.get_chats(identifier="&filter=unread")

            else:
                # Getting custom lists by their ID
                chat_lists = await authed.get_pinned_lists()
                BackLog.info(
                    instance=self,
                    message=f"{self.identifier_name}: Chat Lists: {chat_lists}, delta = {self.delta}",
                )

                # If the specified chat list exists, select chats from this list
                if rules["chat_list"] in chat_lists:
                    BackLog.info(
                        instance=self,
                        message=f"{self.identifier_name}: Selected chat: {rules['chat_list']}, delta = {self.delta}",
                    )
                    if self.delta > 0:
                        return await authed.get_chats(
                            identifier=f"&list_id={str(chat_lists[rules['chat_list']])}",
                            delta=self.delta,
                        )
                    else:
                        return await authed.get_chats(
                            identifier=f"&list_id={str(chat_lists[rules['chat_list']])}"
                        )

        # If 'chat_list' rule does not exist, or if the specified chat list does not exist, select all chats
        BackLog.info(
            instance=self,
            message=f"{self.identifier_name}: Fetching all chats, delta = {self.delta}",
        )
        if self.delta > 0:
            return await authed.get_chats(delta=self.delta)
        else:
            return await authed.get_chats()

    def load_credentials_from_userdata(self, user_data):
        auth_json = {}
        rules = {}

        try:
            if "option" in user_data:
                auth_json = json.loads(user_data["option"])
                BackLog.info(
                    instance=self,
                    message=f"{self.identifier_name}: AUTH_JSON: loaded successfully....",
                )

            if "rules" in user_data:
                rules = json.loads(user_data["rules"])
                BackLog.info(
                    instance=self,
                    message=f"{self.identifier_name}: Rules: loaded successfully.....",
                )

                if "delta" in rules:
                    self.delta = int(rules["delta"])
                    BackLog.info(
                        instance=self,
                        message=f"{self.identifier_name}: Rules: delta = {self.delta}",
                    )

                if "product_limit_per_category" in rules:
                    self.product_limit_per_category = int(
                        rules["product_limit_per_category"]
                    )
                    BackLog.info(
                        instance=self,
                        message=f"{self.identifier_name}: Rules: product limit per category = {self.product_limit_per_category}",
                    )

        except Exception as e:
            BackLog.exception(
                instance=self,
                message=f"{self.identifier_name}: Exception occurred...",
            )

        return auth_json, rules

    async def authenticate(self, api: replica.api_types, auth_json):
        # BackLog.info(
        #     instance=self,
        #     message=f"Type: {type(auth_json)}, Creds: {auth_json}",
        # )
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

    def predict_product_price(self, user_info: dict, product_info: dict) -> float:
        # TODO : Implement a function predicting the price of a product based on user info and product info.
        # self.pricing_model.predict(user_info, product_info)
        return 10

    def get_purchase_history(self, user_id: str, purchased) -> list:
        # TODO : Implement a function fetching for each chat user_id their purchase history in the db.
        # self.db.get_purchase_history(user_id)
        if str(user_id) in purchased:
            return purchased[str(user_id)]
        return []

    def fetch_user_info(self, user_id, purchased) -> dict:
        # TODO : Implement a function fetching for each chat user_id their purchase history in the db.
        # self.db.get_purchase_history(user_id)
        if str(user_id) in purchased:
            return purchased[str(user_id)]
        return purchased

    def fetch_product_info(self, product_id: str, products) -> dict:
        for dictionary in products["products"]:
            if dictionary.get("id") == product_id:
                return dictionary

        return None

    def build_payload_for_Product(self, messages: any):
        payload = {"input": {"search_prod_input": {"history": messages}}}
        return payload

    def build_payload_for_AI(
        self, user_name: str, messages: any, rules, product_message=""
    ):
        prompt_template = ""
        if "prompt_template" in rules:
            prompt_template = product_message + "Character details: \n" \
                              + rules["prompt_template"]
        elif product_message:
            prompt_template = product_message

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
        await self.initialize(user_data=user_data)

        # Get last_message_ids from option
        if "last_message_ids" in option:
            last_message_ids = option["last_message_ids"]
        else:
            last_message_ids = None

        print("Starting product scraping...")
        chats = await self.select_chats(self.authed, self.rules)

        user_id_list = [item["withUser"]["id"] for item in chats]
        all_users_info = {}

        for user_id in user_id_list:
            # get last_message_id in firebase db
            if (
                str(user_id) in last_message_ids
                and "last_message_id" in last_message_ids[str(user_id)]
            ):
                last_message_id = last_message_ids[str(user_id)]["last_message_id"]
            else:
                last_message_id = "0"

            user_info = {}
            try:
                statistics = await self.authed.get_subscriber_info(user_id)
                user_info["statistics"] = statistics

                purchases = await self.authed.get_subscriber_gallery(
                    user_id, None, to_specific_id=last_message_id, limit=40
                )

                purchased_items = []
                for item in purchases:
                    parsed_item = {
                        "message_id": item["message_id"],
                        "price": item["price"],
                        "medias": [item for item in item["media"]],
                        "created": item["createdAt"],
                        "timestamp": item["createdAt"],
                    }
                    purchased_items.append(parsed_item)

                user_info["purchased"] = purchased_items

            except Exception as e:
                BackLog.exception(
                    instance=self,
                    message=f"{self.identifier_name}: Exception occurred...",
                )
                pass

            BackLog.info(
                self,
                f"{self.identifier_name}: Loaded purchased products for {str(user_id)}, {len(user_info['purchased'])}",
            )
            all_users_info[str(user_id)] = user_info

        # await api.close_pools()
        return all_users_info

    async def get_all_products(self, user_data: any, option: any = None):
        await self.initialize(user_data=user_data)

        categories = await self.authed.get_content_categories()

        full_content = []
        label_tasks = []  # This list will store the tasks for labeling the content
        for category in categories:
            offset = 0  # Create an offset variable

            if self.product_limit_per_category > 0:
                content = await self.authed.get_content(
                    category["id"], offset, limit=self.product_limit_per_category
                )
            else:
                content = await self.authed.get_content(
                    category["id"], offset, limit=self.product_limit_per_category
                )

            for item in content:
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
                    print(f"|-- Item: {parsed_item['id']} - {parsed_item['type']}")
                    if parsed_item["type"] == "photo":
                        task = label_content(
                            type=parsed_item["type"],
                            url=parsed_item["full"],
                            k=15,
                            id=parsed_item["id"],
                            item=parsed_item,
                        )
                        label_tasks.append(task)
                except:
                    import traceback

                    print(traceback.print_exc())

        # Label all contents in parallel
        try:
            labels = await asyncio.gather(*label_tasks)
        except Exception as e:
            print(f"Error occurred: {e}")
            import traceback

            print(traceback.print_exc())

        # await api.close_pools()

        BackLog.info(
            self,
            f"{self.identifier_name}: Products: {len(full_content)}, Labels = {len(labels)}",
        )
        return {"products": labels}
