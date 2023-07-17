import json

from core.utils.dict import remove_duplicates
from db.firebase import db


"""
Here 'key' means 'identifier_name' from frontend
"""


def create_products(user_id: str):
    document_ref = db.collection("products").document(user_id)
    document_ref.set({})
    return {"message": "Product created successfully"}


def get_products(user_id: str, provider_name: str, key: str):
    document_ref = db.collection(f"products/{user_id}/{provider_name}").document(key)
    doc = document_ref.get()
    if not doc.exists:
        return {}

    return document_ref.get().to_dict()


def update_products(user_id: str, provider_name: str, key: str, new_content: any):
    document_ref = db.collection(f"products/{user_id}/{provider_name}").document(key)
    doc = document_ref.get()
    if not doc.exists:
        document_ref.set({})

    original_data = document_ref.get().to_dict()

    if new_content == None or new_content == "":
        pass
        # del original_data[provider_name][key]
    else:
        if "products" in original_data:
            original_data["products"] += new_content
        else:
            original_data["products"] = new_content

        original_data["products"] = sorted(
            original_data["products"], key=lambda x: x["id"], reverse=True
        )

        original_data["products"] = remove_duplicates(original_data["products"])
        original_data["last_product_id"] = original_data["products"][0]["id"]

        document_ref.update(original_data)

    return {"message": "Products data updated successfully"}
