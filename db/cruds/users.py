
from core.firebase import db   
from schemas.users import UsersSchema

def create_user(user: UsersSchema):
    user_doc_ref = db.collection("users").document(user.id)
    user_doc_ref.set({
        "username" : user.username,
        "email" : user.email
    })
    return {"message": "User created successfully"}

def get_user(id: str):
    user_doc_ref = db.collection("users").document(id)
    user_doc = user_doc_ref.get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        return user_data
    else:
        return None