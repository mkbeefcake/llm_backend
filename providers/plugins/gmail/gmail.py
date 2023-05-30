import base64
import json
import sys
from email.mime.text import MIMEText
from pathlib import Path

from authlib.integrations.starlette_client import OAuth
from google.oauth2.credentials import Credentials
from google_auth_httplib2 import AuthorizedHttp
from googleapiclient.discovery import build
from starlette.config import Config
from starlette.requests import Request

from providers.base import BaseProvider

SESSION_NAME = "google_user"
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.addons.current.action.compose",
]
MAX_MESSAGES_COUNT = 10

oauth2_crendential_path = Path(".") / "oauth2-credentials.json"
oauth2_credentials = json.load(open(oauth2_crendential_path))
oauth = OAuth()
oauth.register(
    name="google",
    client_id=oauth2_credentials["web"]["client_id"],
    client_secret=oauth2_credentials["web"]["client_secret"],
    access_token_url=oauth2_credentials["web"]["token_uri"],
    access_token_params=None,
    authorize_url=oauth2_credentials["web"]["auth_uri"],
    authorize_params=None,
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "prompt": "consent",
        "scope": "openid email profile https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.compose",
    },
)


class GMailProvider(BaseProvider):
    async def link_provider(self, request: Request):
        request.session.clear()
        redirect_uri = request.url_for("google_auth")
        return await oauth.google.authorize_redirect(
            request, str(redirect_uri), access_type="offline"
        )

    async def get_access_token(self, request: Request) -> str:
        token = await oauth.google.authorize_access_token(request)
        request.session[SESSION_NAME] = token
        return token

    async def get_access_token_from_refresh_token(self, refresh_token: str) -> str:
        creds = Credentials.from_authorized_user_info(
            info={
                "client_id": oauth2_credentials["web"]["client_id"],
                "client_secret": oauth2_credentials["web"]["client_secret"],
                "refresh_token": refresh_token,
            }
        )
        creds.refresh(AuthorizedHttp(credentials=creds))
        return {"access_token": creds.token}

    async def get_session_info(self, request: Request) -> str:
        return request.session[SESSION_NAME]

    def get_profile(self, access_token: str, option: any):
        print(
            "[%s]: get_profile: %s, %s" % (self.plugin_name, access_token, option),
            file=sys.stdout,
        )

    def get_gmail_service(self, access_token: str):
        creds = Credentials(
            token=access_token,
            client_id=oauth2_credentials["web"]["client_id"],
            client_secret=oauth2_credentials["web"]["client_secret"],
            token_uri=oauth2_credentials["web"]["token_uri"],
            scopes=SCOPES,
        )
        gmail_service = build("gmail", "v1", credentials=creds)
        return gmail_service

    def get_last_message(self, access_token: str, option: any):
        gmail_service = self.get_gmail_service(access_token)

        message_list = (
            gmail_service.users()
            .messages()
            .list(userId="me", maxResults=MAX_MESSAGES_COUNT, q=f"from:!me")
            .execute()
        )
        messages = message_list.get("messages", [])
        next_page_token = message_list.get("nextPageToken")

        # get last message
        message_id = messages[0]["id"]
        message = (
            gmail_service.users().messages().get(userId="me", id=message_id).execute()
        )

        # get senders
        senders = []
        subject = ""
        for header in message["payload"]["headers"]:
            if header["name"].lower() == "from":
                senders.append(header["value"])
            if header["name"].lower() == "subject":
                subject = header["value"]

        # get content
        snippet = message["snippet"]
        if "parts" in message["payload"]:
            for part in message["payload"]["parts"]:
                if part["body"] and part["mimeType"] == "text/plain":
                    content = base64.urlsafe_b64decode(part["body"]["data"]).decode()
                    break
        else:
            content = base64.urlsafe_b64decode(
                message["payload"]["body"]["data"]
            ).decode()

        return {
            "messageId": message_id,
            "sender": senders,
            "subject": subject,
            "option": {"nextPageToken": next_page_token},
            "snippet": snippet,
            "html": content,
        }

    # sample from_when='timestamp'
    def get_messages(self, access_token: str, from_when: str, count: int, option: any):
        gmail_service = self.get_gmail_service(access_token)
        message_list = (
            gmail_service.users()
            .messages()
            .list(userId="me", maxResults=count, q=f"after:{from_when} from:!me")
            .execute()
        )
        messages = message_list.get("messages", [])
        next_page_token = message_list.get("nextPageToken")

        results = []
        for m in messages:
            message_id = m["id"]
            message = (
                gmail_service.users()
                .messages()
                .get(userId="me", id=message_id)
                .execute()
            )

            # get senders
            senders = []
            subject = ""
            for header in message["payload"]["headers"]:
                if header["name"].lower() == "from":
                    senders.append(header["value"])
                if header["name"].lower() == "subject":
                    subject = header["value"]

            # get content
            snippet = message["snippet"]

            if "parts" in message["payload"]:
                for part in message["payload"]["parts"]:
                    if part["body"] and part["mimeType"] == "text/plain":
                        content = base64.urlsafe_b64decode(
                            part["body"]["data"]
                        ).decode()
                        break
            else:
                content = base64.urlsafe_b64decode(
                    message["payload"]["body"]["data"]
                ).decode()

            results.append(
                {
                    "messageId": message_id,
                    "sender": senders,
                    "subject": subject,
                    "snippet": snippet,
                    "html": content,
                }
            )

        return {
            "option": {"nextPageToken": next_page_token},
            "messages": results,
        }

    def reply_to_message(self, access_token: str, to: str, message: str, option: any):
        gmail_service = self.get_gmail_service(access_token)

        message_id = to
        old_message = (
            gmail_service.users().messages().get(userId="me", id=message_id).execute()
        )

        # get senders
        senders = []
        subject = ""
        for header in old_message["payload"]["headers"]:
            if header["name"].lower() == "from":
                senders.append(header["value"])
            if header["name"].lower() == "subject":
                subject = header["value"]

        reply_message = f"Replying to {senders}\n\n{message}"
        new_message = MIMEText(reply_message)
        new_message["to"] = senders[0]
        new_message["subject"] = f"Re: {subject}"
        new_message["Reference"] = message_id
        new_message["In-Reply-To"] = message_id
        create_message = {
            "raw": base64.urlsafe_b64encode(new_message.as_bytes()).decode()
        }
        send_message = (
            gmail_service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        return {"message": "Email sent!"}

    def disconnect(self, request: Request):
        pass

    pass
