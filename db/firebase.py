import json
from pathlib import Path

import firebase_admin
import pyrebase
import requests
from firebase_admin import auth, credentials, firestore, storage

service_account_path = Path(".") / "chat-automation-serviceaccount.json"
firebase_config_path = Path(".") / "chat-automation-firebase.json"

# initialize Firestore credentials
cred = credentials.Certificate(service_account_path)
firebase_admin.initialize_app(
    cred, {"storageBucket": "chat-automation-387710.appspot.com"}
)

# firebase app
pb = pyrebase.initialize_app(json.load(open(firebase_config_path)))

# create Firestore client instance
db = firestore.client()


def authenticate_user(email: str, password: str):
    auth_user = pb.auth().sign_in_with_email_and_password(email, password)
    return auth_user["idToken"]


def decode_access_token(token: str):
    user = auth.verify_id_token(token)
    return user


def create_user(email: str, password: str):
    user = pb.auth().create_user_with_email_and_password(email=email, password=password)
    result = pb.auth().send_email_verification(user["idToken"])
    return result


def load_json_from_storage(file_name):
    try:
        bucket = storage.bucket()
        blob = bucket.blob(file_name)
        json_data = blob.download_as_text()

        print(f"Successed to load {file_name}")
        return json.loads(json_data)

    except Exception as e:
        print(f"Failed to load {file_name}")
        return None


def save_json_to_storage(json_data, file_name):
    try:
        bucket = storage.bucket()
        blob = bucket.blob(file_name)
        blob.upload_from_string(json.dumps(json_data), content_type="application/json")
        print(f"Succeeded to save {file_name}")

    except Exception as e:
        print(f"Failed to save {file_name}")
        pass
