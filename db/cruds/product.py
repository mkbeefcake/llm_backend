import json

from core.utils.dict import remove_duplicates
from core.utils.timestamp import get_current_timestamp
from db.firebase import db, load_json_from_storage, save_json_to_storage


"""
Here 'key' means 'identifier_name' from frontend
"""


def get_products(user_id: str, provider_name: str, key: str):
    filename = f"{user_id}/{provider_name}/{key}/products.json"
    products = load_json_from_storage(filename)
    return products


def update_products(user_id: str, provider_name: str, key: str, new_content: any):
    previous_products = get_products(user_id, provider_name, key)

    products = previous_products + new_content
    products = sorted(products, key=lambda x: x["id"], reverse=True)

    products = remove_duplicates(products)

    filename = f"{user_id}/{provider_name}/{key}/products.json"
    save_json_to_storage(products, filename)
