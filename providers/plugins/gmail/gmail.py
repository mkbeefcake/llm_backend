import sys
from providers.base import BaseProvider
import json
from pathlib import Path

from starlette.config import Config
from starlette.requests import Request

from authlib.integrations.starlette_client import OAuth

SESSION_NAME = "google_user"

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
        'scope': 'openid email profile'
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
        return userinfo

    def get_profile(self, access_token: str, option: any):
        print("[%s]: get_profile: %s, %s" % (self.plugin_name, access_token, option), file=sys.stdout)
    
    def get_last_message(self, access_token: str, option: any):
        print("[%s]: get_last_message: %s, %s" % (self.plugin_name, access_token, option), file=sys.stdout)

    def get_messages(self, access_token: str, from_when: str, option: any):
        print("[%s]: get_messages: %s %s, %s" % (self.plugin_name, access_token, from_when, option), file=sys.stdout)
     
    def disconnect(self, request:Request):
        pass

    pass