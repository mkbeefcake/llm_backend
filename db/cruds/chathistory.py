import json

from core.utils.dict import remove_duplicates
from db.firebase import db


"""
Here 'key' means 'identifier_name' from frontend
"""


def create_chat_histories(user_id: str):
    document_ref = db.collection("chat_histories").document(user_id)
    document_ref.set({})
    return {"message": "Chat history created successfully"}


def get_chat_histories(user_id: str, provider_name: str, key: str):
    document_ref = db.collection(f"chat_histories/{user_id}/{provider_name}").document(
        key
    )
    doc = document_ref.get()
    if not doc.exists:
        return {}

    return document_ref.get().to_dict()


def update_chat_histories(user_id: str, provider_name: str, key: str, new_content: any):
    document_ref = db.collection(f"chat_histories/{user_id}/{provider_name}").document(
        key
    )
    doc = document_ref.get()
    if not doc.exists:
        document_ref.set({})

    original_data = document_ref.get().to_dict()

    if new_content == None or new_content == "":
        pass
    else:
        if "chats" in original_data:
            original_data["chats"] += new_content
        else:
            original_data["chats"] = new_content

        original_data["chats"] = sorted(
            original_data["chats"], key=lambda x: x["id"], reverse=True
        )

        original_data["chats"] = remove_duplicates(original_data["chats"])
        document_ref.update(original_data)

    return {"message": "Chat history data updated successfully"}
