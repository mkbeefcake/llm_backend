import firebase_admin
import pyrebase
import json
import requests

from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth
from pathlib import Path

service_account_path = Path(".") / "neo-chatbot-f0fff-service_account_keys.json"
firebase_config_path = Path(".") / "neo-chatbot-firebase.json"

# initialize Firestore credentials
cred = credentials.Certificate(service_account_path)
firebase_admin.initialize_app(cred)

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
