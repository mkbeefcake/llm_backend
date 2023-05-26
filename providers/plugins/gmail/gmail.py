import sys
import json
import base64

from providers.base import BaseProvider
from pathlib import Path

from starlette.config import Config
from starlette.requests import Request

from authlib.integrations.starlette_client import OAuth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SESSION_NAME = "google_user"
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.addons.current.action.compose'
]
MAX_MESSAGES_COUNT=10

oauth2_crendential_path = Path(".") / "oauth2-credentials.json"
oauth2_credentials = json.load(open(oauth2_crendential_path))
oauth = OAuth()
oauth.register(
    name='google',
    client_id=oauth2_credentials["web"]["client_id"],
    client_secret=oauth2_credentials["web"]["client_secret"],
    access_token_url=oauth2_credentials["web"]["token_uri"],
    access_token_params=None,
    authorize_url=oauth2_credentials["web"]["auth_uri"],
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.compose'
    }
)

class GMailProvider(BaseProvider):

    async def link_provider(self, request: Request):
        request.session.clear()
        redirect_uri = request.url_for("google_auth")
        return await oauth.google.authorize_redirect(request, str(redirect_uri))

    async def get_access_token(self, request:Request) -> str:
        token = await oauth.google.authorize_access_token(request)
        userinfo = token['userinfo']
        return token

    def get_profile(self, access_token: str, option: any):
        print("[%s]: get_profile: %s, %s" % (self.plugin_name, access_token, option), file=sys.stdout)
    
    def get_last_message(self, access_token: str, option: any):
        creds = Credentials(token=access_token, 
                            client_id=oauth2_credentials["web"]["client_id"],
                            client_secret=oauth2_credentials["web"]["client_secret"],
                            token_uri=oauth2_credentials["web"]["token_uri"],
                            scopes=SCOPES
                            )
        gmail_service = build('gmail', 'v1', credentials=creds)
        message_list = gmail_service.users().messages().list(userId='me', maxResults=MAX_MESSAGES_COUNT).execute()
        messages = message_list.get('messages', [])
        next_page_token = message_list.get('nextPageToken')
        message_id = messages[0]['id']
        message = gmail_service.users().messages().get(userId='me', id=message_id).execute()

        snippet = message['snippet']
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['body'] and part['mimeType'] == 'text/plain':
                    content = base64.urlsafe_b64decode(part['body']['data']).decode()
                    break
        else:
            content = base64.urlsafe_b64decode(message['payload']['body']['data']).decode()


        return {'messageId': message_id, "option": {"nextPageToken": next_page_token}, 'snippet': snippet, "content": content }

    def get_messages(self, access_token: str, from_what: str, count: int, option: any):
        creds = Credentials(token=access_token, 
                            client_id=oauth2_credentials["web"]["client_id"],
                            client_secret=oauth2_credentials["web"]["client_secret"],
                            token_uri=oauth2_credentials["web"]["token_uri"],
                            scopes=SCOPES
                            )
        gmail_service = build('gmail', 'v1', credentials=creds)
        message_list = gmail_service.users().messages().list(userId='me', maxResults=count, q=f"{from_what}").execute()

        messages = message_list.get('messages', [])
        next_page_token = message_list.get('nextPageToken')

        results = []
        for m in messages:
            message_id = m['id']
            message = gmail_service.users().messages().get(userId='me', id=message_id).execute()

            snippet = message['snippet']
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['body'] and part['mimeType'] == 'text/plain':
                        content = base64.urlsafe_b64decode(part['body']['data']).decode()
                        break
            else:
                content = base64.urlsafe_b64decode(message['payload']['body']['data']).decode()


            results.append({'messageId': message_id, 'snippet': snippet, "content": content })

        return {"option": {"nextPageToken": next_page_token}, "messages": results, }

    def disconnect(self, request:Request):
        pass

    pass