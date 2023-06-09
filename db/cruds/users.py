import json

from firebase_admin import firestore

from core.firebase import db
from db.schemas.users import UsersSchema


def create_user(user: UsersSchema):
    user_doc_ref = db.collection("users").document(user.id)
    user_doc_ref.set({})
    return {"message": "User created successfully"}


def update_user(user: UsersSchema, provider_name: str, key: str, content: str):
    user_doc_ref = db.collection("users").document(user.id)
    user_data = get_user_data(user.id)

    if not user_data:
        create_user(user=user)
        user_data = {}
    if not provider_name in user_data:
        user_data[provider_name] = {}
    if not key in user_data[provider_name]:
        user_data[provider_name][key] = {}

    if content == "":
        del user_data[provider_name][key]
    else:
        user_data[provider_name][key] = json.loads(content)

    # if content == "":
    #     user_doc_ref.update({(provider_name, key): firestore.DELETE_FIELD})
    user_doc_ref.update(
        {
            provider_name: user_data[provider_name],
        }
    )
    return {"message": "User updated successfully"}


def get_user_data(id: str):
    user_doc_ref = db.collection("users").document(id)
    user_doc = user_doc_ref.get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        return user_data
    else:
        return None


def get_user_providers(id: str):
    user_doc_ref = db.collection("users").document(id)
    user_doc = user_doc_ref.get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        return list(user_data.keys())
    else:
        return None
