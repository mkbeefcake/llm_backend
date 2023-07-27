import json

from core.utils.dict import remove_duplicates
from db.firebase import db, load_json_from_storage, save_json_to_storage


"""
Here 'key' means 'identifier_name' from frontend
"""


def get_last_message_ids(user_id: str, provider_name: str, key: str):
    purchased = get_purchased(user_id, provider_name, key)

    last_message_ids = {}
    for chatuser_id in purchased:
        if "purchased" in purchased[chatuser_id] and len(
            purchased[chatuser_id]["purchased"]
        ):
            if "message_id" in purchased[chatuser_id]["purchased"]:
                last_message_ids[chatuser_id] = purchased[chatuser_id]["purchased"][0][
                    "message_id"
                ]

    return last_message_ids


def get_purchased(user_id: str, provider_name: str, key: str):
    filename = f"{user_id}/{provider_name}/{key}/purchased.json"
    purchased = load_json_from_storage(filename)
    return purchased


def update_purchased(user_id: str, provider_name: str, key: str, new_content: any):
    purchased = get_purchased(user_id, provider_name, key)

    for chatuser_id in purchased:
        if chatuser_id in new_content and "statistics" in new_content[chatuser_id]:
            purchased[chatuser_id]["statistics"] = new_content[chatuser_id][
                "statistics"
            ]

        if chatuser_id in new_content and "purchased" in new_content[chatuser_id]:
            purchased[chatuser_id]["purchased"] = (
                purchased[chatuser_id]["purchased"]
                + new_content[chatuser_id]["purchased"]
            )
            purchased[chatuser_id]["purchased"] = sorted(
                purchased[chatuser_id]["purchased"],
                key=lambda x: x["message_id"],
                reverse=True,
            )
            purchased[chatuser_id]["purchased"] = remove_duplicates(
                purchased[chatuser_id]["purchased"], by="message_id"
            )

    for chatuser_id in new_content:
        if chatuser_id not in purchased:
            purchased[chatuser_id] = new_content[chatuser_id]

    filename = f"{user_id}/{provider_name}/{key}/purchased.json"
    save_json_to_storage(purchased, filename)
