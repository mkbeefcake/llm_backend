import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from pathlib import Path

cert_path = Path(".") / "neo-chatbot-f0fff-firebase-adminsdk.json"

# initialize Firestore credentials
cred = credentials.Certificate(cert_path)
firebase_admin.initialize_app(cred)

# create Firestore client instance
db = firestore.client()
