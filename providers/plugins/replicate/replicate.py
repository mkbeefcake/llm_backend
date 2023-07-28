import asyncio
import io
import json
import os
import random
import re
import threading
import unicodedata

import imageio
import numpy as np
import replica
import requests
from fastapi.templating import Jinja2Templates
from PIL import Image
from starlette.requests import Request

from core.utils.http import http_get_bytes, http_post_file
from core.utils.log import BackLog
from core.utils.timestamp import get_current_timestamp
from products.pinecone import pinecone_service
from providers.base import BaseProvider
from services.service import replica_service, textgen_service

templates = Jinja2Templates(directory="templates/replicate")
PRODUCT_REPLICA_ENDPOINT = os.getenv("PRODUCT_REPLICA_ENDPOINT")
PRODUCT_REPLICA_ENDPOINT_NEW = os.getenv("PRODUCT_REPLICA_ENDPOINT_NEW")


def char_is_emoji(character):
    return unicodedata.category(character) in ["So", "Sm"]


def find_element_by_id(array, id):
    for element in array:
        if element.get("id") == id:
            return element
    return None


def remove_abrupt_sentences(text):
    # Split the text into sentences based on the presence of .!? as potential sentence delimiters
    sentences = re.split(r"(?<=[.!?])\s+", text)

    # List to store complete sentences
    complete_sentences = []

    # Loop over sentences
    for sentence in sentences:
        # If the sentence does not end with a punctuation mark or an emoji
        if sentence[-1] in ".?!" or char_is_emoji(sentence[-1]):
            complete_sentences.append(sentence)

    # Join the complete sentences back into a single text
    cleaned_text = " ".join(complete_sentences)

    return cleaned_text


def control_ai_response(string):
    # Remove content between asterisks
    string = re.sub(r"\*.*?\*", "", string)

    # Remove content between parentheses
    string = re.sub(r"\(.*?\)", "", string)

    # Remove trailing lines

    string = remove_abrupt_sentences(string)

    return string


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


class ReplicateProvider(BaseProvider):
    product_caches = {}

    def __init__(self) -> None:
        super().__init__()
        self.num_messages = 10
        self.initialized = False
        self.initializing = False
        self.api = None
        self.delta = 0
        self.product_limit_per_category = 0
        self.bot_tasks = {}

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

    async def disconnect(self, request: Request):
        if self.api != None and self.initialized == True:
            await self.api.close_pools()
            self.initialized = False
        pass

    async def initialize(self, user_data: any):
        # lock threading
        count = 0
        while self.initializing == True and count < 4:
            await asyncio.sleep(1)
            count = count + 1

        if self.initialized == True:
            return self.initialized

        try:
            self.initializing = True
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

        except Exception as e:
            BackLog.exception(
                instance=self,
                message=f"{self.identifier_name}: Failed authenticate() function.....",
            )
            self.initializing = False
            pass

        finally:
            self.initializing = False

        return self.initialized

    def finalize(self):
        if self.api:
            self.api = None
        if self.auth_json:
            self.auth_json = None
        if self.rules:
            self.rules = None
        if self.authed:
            self.authed = None

    def update_provider_info(self, user_data: any, option: any = None):
        self.auth_json, self.rules = self.load_credentials_from_userdata(user_data)
        pass

    async def process_user_chat(self, chat, user_data, option):
        user = await self.authed.get_user(chat["withUser"]["id"])

        try:
            if not user.isPerformer:
                # BackLog.info(
                #     instance=self,
                #     message=f"{self.identifier_name}: Checking user: {user.name}",
                # )

                # fetch user's messages
                messages, last_message_role = await self.fetch_messages(
                    user, self.authed
                )
                if last_message_role == "user":
                    BackLog.info(
                        instance=self,
                        message=f"{self.identifier_name}: Replying to user: {user.name}",
                    )
                    # suggest product from ai
                    payload_product = self.build_payload_for_Product(messages=messages)
                    suggested_products = replica_service.suggest_product(
                        messages=messages, option=payload_product
                    )
                    BackLog.info(
                        instance=self,
                        message=f"{self.identifier_name}: Suggested Product from AI: {suggested_products}",
                    )

                    try:
                        suggested_products["search_product_processed"][
                            "product_intent"
                        ] == True
                        sell_product = True
                    except:
                        sell_product = False

                    # if a product is suggested, we match it in the db and retrieve the product id
                    if sell_product == True:
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
                            message=f"{self.identifier_name}: Has purchased history: {product_history is not None}",
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
                            message=f"{self.identifier_name}: User has Purchased: {user_info is not None}",
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

                        # build product message
                        product_message = f'(You have to convince the user {user.name} to buy a {suggested_products["search_product_processed"]["product_description"]} photo of you for {product_price}$. You want the money)'
                    else:
                        product_id = []
                        product_message = ""
                        product_price = 0

                    """ OLD SERVICE 
                    # build payload & get ai response
                    payload_ai = self.build_payload_for_AI(
                        user_name=user.name,
                        messages=messages,
                        rules=self.rules,
                        product_message=product_message,
                    )

                    """

                    # TODO : Refactor ASAP
                    history, user_input = await self.format_text_gen_messages(
                        messages, user
                    )

                    BackLog.info(
                        instance=self,
                        message=f"{self.identifier_name}: Last message from Ricardo : {user_input}, Last 10  {history}",
                    )

                    # For testing purposes
                    # user_input = "what's your favorite landmark there ?"
                    # history = ['hey slut', 'hey babe', 'horny my bitch ?', 'OMG YES! SO MUCH IT HURTS!', "where you living my slut ? ", "i live in los angeles baby" ]

                    ai_response = textgen_service.get_response(
                        user_input=user_input + " " + product_message,
                        history=history,
                        username=user.name,
                    )

                    # Parse ai response
                    ai_response = control_ai_response(ai_response)

                    BackLog.info(
                        instance=self,
                        message=f"{self.identifier_name}: Response from AI: {ai_response}",
                    )

                    # post ai message to user
                    print(
                        type(product_price),
                    )

                    # response = await self.post_message(
                    #     user,
                    #     self.authed,
                    #     ai_response,
                    #     price=product_price,
                    #     mediaFiles=[product_id],
                    # )

                    # BackLog.info(
                    #     instance=self,
                    #     message=f"{self.identifier_name}: Sending message. Status code: {response}",
                    # )

                    BackLog.info(
                        instance=self,
                        message=f"{self.identifier_name}: Processed chat for {user.name} successfully",
                    )
                else:
                    # BackLog.info(
                    #     instance=self,
                    #     message=f"{self.identifier_name}: No new messages from {user.name}. Skipping...",
                    # )
                    pass

        except Exception as e:
            BackLog.exception(
                instance=self,
                message=f"{self.identifier_name}: Exception occurred...",
            )

        finally:
            del self.bot_tasks[chat["withUser"]["id"]]

    async def start_autobot(self, user_data: any, option: any):
        if await self.initialize(user_data=user_data) != True:
            return

        # Select relevant chats
        chats = await self.select_chats(self.authed, self.rules, interval=300, limit=10)

        new_chats = 0
        for chat in chats:
            try:
                # check last messages from chat, if last message is from other, please go on
                if (
                    chat["lastMessage"]["fromUser"]["id"] == chat["withUser"]["id"]
                    and not chat["withUser"]["id"] in self.bot_tasks
                ):
                    task = asyncio.create_task(
                        self.process_user_chat(chat, user_data, option)
                    )
                    self.bot_tasks[chat["withUser"]["id"]] = task
                    new_chats = new_chats + 1
            except:
                import traceback

                print(traceback.print_exc())

        BackLog.info(
            instance=self,
            message=f"{self.identifier_name}: Detected {new_chats} new chats and current {len(self.bot_tasks)} chats processing....",
        )

        # await api.close_pools()

    async def label_content(self, type, url, k, id, item, semaphore):
        async with semaphore:
            try:
                if id in ReplicateProvider.product_caches:
                    return ReplicateProvider.product_caches[id]

                endpoint = PRODUCT_REPLICA_ENDPOINT

                if type == "photo":
                    file_content = await http_get_bytes(url)
                    payload = {
                        "k": str(k),
                        "type": type,
                    }
                    response_json = await http_post_file(
                        endpoint, bytes=file_content, params=payload
                    )
                    product = {
                        "id": id,
                        "label": aggregate_labels(response_json),
                        "category": item["category"],
                        "categoryId": item["categoryId"],
                        "createdAt": item["created"],
                        # "type": item["type"],
                        # "full": item["full"],
                    }

                elif type == "video":
                    print(
                        f"|---- Identifier: {self.identifier_name} VideoItem: {id} Starting to read ......"
                    )
                    vidcap = imageio.get_reader(url, "ffmpeg")

                    # Get the total number of frames
                    total_frames = vidcap.count_frames()

                    # Get the frame numbers we want to capture
                    frames_to_capture = np.linspace(0, total_frames - 1, 3, dtype=int)

                    predictions = []
                    for frame_number in frames_to_capture:
                        # Get the specific frame
                        frame = vidcap.get_data(frame_number)
                        image = Image.fromarray(frame)
                        jpeg_bytes = io.BytesIO()
                        image.save(jpeg_bytes, format="JPEG")
                        jpeg_bytes = jpeg_bytes.getvalue()

                        print(
                            f"|------ VideoItem: {id} - Frame/Total: {frame_number}/{total_frames}"
                        )
                        # Process the frame with your model
                        payload = {
                            "k": k,
                            "type": "photo",
                        }
                        response = requests.post(
                            endpoint, files={"file": jpeg_bytes}, data=payload
                        )

                        prediction = response.json()

                        print(
                            f"|------ VideoItem: {id} - Frame/Total: {frame_number}/{total_frames} tagging Done!"
                        )
                        predictions.append(prediction)

                    # Create a list of keys that are common in all predictions
                    final_prediction = {}
                    for d in predictions:
                        final_prediction.update(d)

                    product = {
                        "id": id,
                        "label": aggregate_labels(final_prediction),
                        "category": item["category"],
                        "categoryId": item["categoryId"],
                        "createdAt": item["created"],
                        # "type": item["type"],
                        # "full": item["full"],
                    }

                ReplicateProvider.product_caches[id] = product
                return product

            except Exception as e:
                BackLog.exception(
                    instance=None,
                    message=f"Failed to call replica tagging service: url {url}",
                )
                return None

    async def select_chats(self, authed, rules, interval: int = 0, limit: int = 100):
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
                    message=f"{self.identifier_name}: Fetching unread chats, delta = {self.delta}, interval = {interval}, limit = {limit}",
                )
                # if self.delta > 0:
                #     return await authed.get_chats(
                #         identifier="&filter=unread",
                #         delta=self.delta,
                #         interval=interval,
                #         limit=limit,
                #     )
                # else:
                return await authed.get_chats(
                    identifier="&filter=unread", interval=interval, limit=limit
                )

            else:
                # Getting custom lists by their ID
                chat_lists = await authed.get_pinned_lists()

                # If the specified chat list exists, select chats from this list
                if rules["chat_list"] in chat_lists:
                    BackLog.info(
                        instance=self,
                        message=f"{self.identifier_name}: Selected chat: {rules['chat_list']}, delta = {self.delta}, interval = {interval}, limit = {limit}",
                    )
                    # if self.delta > 0:
                    #     return await authed.get_chats(
                    #         identifier=f"&list_id={str(chat_lists[rules['chat_list']])}",
                    #         delta=self.delta,
                    #         interval=interval,
                    #         limit=limit,
                    #     )
                    # else:
                    return await authed.get_chats(
                        identifier=f"&list_id={str(chat_lists[rules['chat_list']])}",
                        interval=interval,
                        limit=limit,
                    )

        BackLog.info(
            instance=self,
            message=f"{self.identifier_name}: Fetching all chats, delta = {self.delta}, interval = {interval}, limit={limit}",
        )

        # if self.delta > 0:
        #     return await authed.get_chats(delta=self.delta, limit=limit, interval=interval)
        # else:
        return await authed.get_chats(limit=limit, interval=interval)

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
            fetched_messages = await user.get_message(
                last_message=last_message_id, limit=100
            )

            if not fetched_messages["list"]:
                break

            for message in fetched_messages["list"]:
                if message["fromUser"]["id"] == user.id:
                    value = {"role": "user", "content": message["text"]}
                else:
                    value = {"role": "assistant", "content": message["text"]}

                messages.append(value)

            last_message_id = fetched_messages["list"][-1]["id"]

        last_message_role = messages[0]["role"]

        # Put message in right order
        messages = messages[::-1]

        return messages, last_message_role

    async def scrap_messages(self, chat, semaphore):
        async with semaphore:
            try:
                user = await self.authed.get_user(chat["withUser"]["id"])
                if not user.isPerformer:
                    data = await self.authed.get_subscriber_info(user.id)
                    if data["totalSumm"] > 20:  # Filter by LTV
                        # fetch user's messages
                        messages = []
                        last_message_id = None

                        while len(messages) < 1000:
                            fetched_messages = await user.get_message(
                                last_message=last_message_id, limit=100
                            )

                            if not fetched_messages["list"]:
                                break

                            for message in fetched_messages["list"]:
                                value = {
                                    "fromUser": message["fromUser"]["id"],
                                    "text": message["text"],
                                    "price": message["price"],
                                    "isOpened": message["isOpened"],
                                    "mediaCount": message["mediaCount"],
                                    "createdAt": message["createdAt"],
                                    "toUser": user.id,
                                }
                                messages.append(value)

                            last_message_id = fetched_messages["list"][-1]["id"]

                        # Put message in right order
                        messages = messages[::-1]
                        BackLog.info(
                            self,
                            f"{self.identifier_name}: Get chat for {user.name}, messages = {len(messages)}...",
                        )
                        return messages
                else:
                    BackLog.info(
                        self,
                        f"{self.identifier_name}: Skip {user.name}...",
                    )
                    return []
            except:
                import traceback

                print(traceback.print_exc())
                return []

    async def format_text_gen_messages(self, messages, user):
        messages = []
        last_message_id = None
        last_role = None
        last_message = ""

        while len(messages) < self.num_messages:
            fetched_messages = await user.get_message(last_message=last_message_id)
            for message in fetched_messages["list"]:
                if message["fromUser"]["id"] == user.id:
                    role = "user"
                else:
                    role = "assistant"

                content = message["text"]

                if last_role == role and messages:
                    messages[-1]["content"] += "\n" + content
                else:
                    messages.append({"role": role, "content": content})

            last_message_id = fetched_messages["list"][-1]["id"]
            if not fetched_messages["list"]:
                break

        # Convert messages in correct order
        messages = messages[::-1]

        # Ensure the last message is from user and
        if messages and messages[-1]["role"] == "user":
            last_message = messages[-1]["content"]
            messages.pop(-1)

        messages = [message["content"] for message in messages]

        return messages, last_message

    def predict_product_price(self, user_info: dict, product_info: dict) -> float:
        # TODO : Implement a function predicting the price of a product based on user info and product info.
        # self.pricing_model.predict(user_info, product_info)
        return random.randint(7, 20) / 2

    def get_purchase_history(self, user_id: str, purchased) -> list:
        # TODO : Implement a function fetching for each chat user_id their purchase history in the db.
        # self.db.get_purchase_history(user_id)
        if purchased is not None and str(user_id) in purchased:
            return purchased[str(user_id)]
        return []

    def fetch_user_info(self, user_id, purchased) -> dict:
        # TODO : Implement a function fetching for each chat user_id their purchase history in the db.
        # self.db.get_purchase_history(user_id)
        if purchased is not None and str(user_id) in purchased:
            return purchased[str(user_id)]
        return purchased

    def fetch_product_info(self, product_id: str, products) -> dict:
        if products is not None and "products" in products:
            for dictionary in products["products"]:
                if dictionary.get("id") == product_id:
                    return dictionary

        return None

    def build_payload_for_TextGen(self, messages: any) -> dict:
        """GOAL: Concatenate messages into an alternate dialog."""
        payload = {"input": {"text_gen_input": {"history": messages}}}
        return payload

    def build_payload_for_Product(self, messages: any):
        payload = {"input": {"search_prod_input": {"history": messages}}}
        return payload

    def build_payload_for_AI(
        self, user_name: str, messages: any, rules, product_message=""
    ):
        prompt_template = ""
        if "prompt_template" in rules:
            prompt_template = (
                product_message + "Character details: \n" + rules["prompt_template"]
            )
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
            response = await authed.send_message(
                user_id=user.id, text=response, price=price, mediaFiles=mediaFiles
            )
            return response
        except Exception:
            import traceback

            print(traceback.format_exc())

    async def scrapy_all_chats(self, user_data: any, option: any = None):
        if await self.initialize(user_data=user_data) != True:
            return

        # Select all chats
        chats = await self.select_chats(self.authed, self.rules)
        BackLog.info(
            self,
            f"{self.identifier_name}: Total chats: {len(chats)}...",
        )

        chat_histories = []
        tasks = []

        start_timestamp = get_current_timestamp()
        BackLog.info(
            instance=self, message=f"Running Scraping task...{start_timestamp}"
        )

        semaphore = asyncio.Semaphore(15)
        for chat in chats:
            tasks.append(asyncio.create_task(self.scrap_messages(chat, semaphore)))

        messages = await asyncio.gather(*tasks)
        end_timestamp = get_current_timestamp()
        BackLog.info(instance=self, message=f"Ended Scraping task...{end_timestamp}")

        tasks = []
        for message in messages:
            chat_histories.extend(message)

        return chat_histories

    async def _get_purchased_task(self, last_message_ids, user_id, semaphore):
        async with semaphore:
            BackLog.info(
                self,
                f"{self.identifier_name}: Started purchased products for {str(user_id)}....",
            )

            # get last_message_id in firebase db
            if str(user_id) in last_message_ids:
                last_message_id = last_message_ids[str(user_id)]
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

                BackLog.info(
                    self,
                    f"{self.identifier_name}: Loaded purchased products for {str(user_id)}, {len(user_info['purchased'])}",
                )
                return (str(user_id), user_info)

            except Exception as e:
                BackLog.exception(
                    instance=self,
                    message=f"{self.identifier_name}: Exception occurred...",
                )
                return (str(user_id), None)

    async def get_purchased_products(self, user_data: any, option: any = None):
        if await self.initialize(user_data=user_data) != True:
            return

        last_message_ids = option["last_message_ids"]

        # Select all chats
        chats = await self.select_chats(self.authed, self.rules)
        BackLog.info(
            self,
            f"{self.identifier_name}: Total chats: {len(chats)}...",
        )

        user_id_list = [item["withUser"]["id"] for item in chats]
        all_users_info = {}
        tasks = []

        start_timestamp = get_current_timestamp()
        BackLog.info(
            instance=self,
            message=f"Running Purchased task...{start_timestamp}, {len(user_id_list)} users",
        )

        semaphore = asyncio.Semaphore(50)
        for user_id in user_id_list:
            tasks.append(
                asyncio.create_task(
                    self._get_purchased_task(last_message_ids, user_id, semaphore)
                )
            )

        results = await asyncio.gather(*tasks)
        end_timestamp = get_current_timestamp()
        BackLog.info(instance=self, message=f"Ended Purchased task...{end_timestamp}")

        tasks = []
        for key, value in results:
            if value is not None:
                all_users_info[key] = value

        # await api.close_pools()
        return all_users_info

    async def _get_all_products(self, category, last_products_ids, semaphore):
        async with semaphore:
            full_content = []
            labels = []
            tasks = []

            offset = 0  # Create an offset variable

            last_product_id = 0
            if category["id"] in last_products_ids:
                last_product_id = int(last_products_ids[category["id"]])

            content = await self.authed.get_content(
                category["id"],
                offset,
                limit=self.product_limit_per_category,
                last_product_id=last_product_id,
            )

            semaphore1 = asyncio.Semaphore(10)
            for item in content:
                parsed_item = {
                    "categoryId": category["id"],
                    "category": category["name"],
                    "id": item["id"],
                    "type": item["type"],
                    "created": item["createdAt"],
                    "full": item["full"],
                }
                full_content.append(parsed_item)

                # Add a task to label this content
                try:
                    print(
                        f"|-- Identifier: {self.identifier_name} Item: {parsed_item['id']} - {parsed_item['type']}"
                    )
                    if parsed_item["type"] == "photo":
                        tasks.append(
                            asyncio.create_task(
                                self.label_content(
                                    type=parsed_item["type"],
                                    url=parsed_item["full"],
                                    k=15,
                                    id=parsed_item["id"],
                                    item=parsed_item,
                                    semaphore=semaphore1,
                                )
                            )
                        )

                    if len(tasks) >= 10:
                        middle_results = await asyncio.gather(*tasks)
                        results = []
                        for element in middle_results:
                            if element is not None:
                                results.append(element)

                        labels.extend(results)
                        tasks = []
                except:
                    import traceback

                    print(traceback.print_exc())
                    pass

        BackLog.info(
            self,
            f"{self.identifier_name}: Products: {len(full_content)}, Labels = {len(labels)}",
        )
        return labels

    async def get_all_products(self, user_data: any, option: any = None):
        if await self.initialize(user_data=user_data) != True:
            return

        last_products_ids = option["last_products_ids"]

        categories = await self.authed.get_content_categories()

        labels = []
        label_tasks = []  # This list will store the tasks for labeling the content

        start_timestamp = get_current_timestamp()
        BackLog.info(
            instance=self, message=f"Running Products task...{start_timestamp}"
        )

        semaphore = asyncio.Semaphore(10)
        for category in categories:
            label_tasks.append(
                asyncio.create_task(
                    self._get_all_products(category, last_products_ids, semaphore)
                )
            )

        labels = await asyncio.gather(*label_tasks)
        total_labels = [element for one in labels for element in one]

        end_timestamp = get_current_timestamp()
        BackLog.info(
            instance=self,
            message=f"Ended Products task...{end_timestamp}, total Labels = {len(total_labels)}",
        )
        return {"products": total_labels}
