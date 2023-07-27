import json

from core.utils.dict import remove_duplicates
from db.firebase import db, load_json_from_storage, save_json_to_storage


"""
Here 'key' means 'identifier_name' from frontend
"""


def get_chat_histories(user_id: str, provider_name: str, key: str):
    filename = f"{user_id}/{provider_name}/{key}/chathistory.json"
    chathistory = load_json_from_storage(filename)
    return chathistory


def update_chat_histories(user_id: str, provider_name: str, key: str, new_content: any):
    filename = f"{user_id}/{provider_name}/{key}/chathistory.json"
    save_json_to_storage(new_content, filename)
