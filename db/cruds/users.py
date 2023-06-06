import json

from firebase_admin import firestore

from core.firebase import db
from db.schemas.users import UsersSchema


def create_user(user: UsersSchema):
    user_doc_ref = db.collection("users").document(user.id)
    user_doc_ref.set({"email": user.email})
    return {"message": "User created successfully"}


def update_user(user: UsersSchema, key: str, content: str):
    user_doc_ref = db.collection("users").document(user.id)

    if content == "":
        user_doc_ref.update({(key): firestore.DELETE_FIELD})
    else:
        user_doc_ref.update(
            {
                key: json.loads(content),
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
