from pathlib import Path
import base64
import json
import sys

from email.mime.text import MIMEText
from pathlib import Path
from urllib.parse import urlencode
from starlette.requests import Request

from providers.nango import NangoProvider


class GoogleAdsProvider(NangoProvider):

    def __init__(self):
        self.sync_time = -1
        self.access_token = None
        self.refresh_token = None
        self.user_data = None
        pass

    def get_provider_info(self):
        return {
            "provider": GoogleAdsProvider.__name__.lower(),
            "short_name": "GoogleAds",
            "provider_description": "GoogleAds Provider",
            "provider_icon_url": "/google-ads.svg",
            "provider_type": "nango",
            "provider_unique_key": "google-ads"
        }

    async def link_provider(self, redirect_url: str, request: Request):
        pass

    def update_provider_info(self, user_data: any, option: any = None):
        print(f"user_data: {user_data}")
        tokens = self.get_credential_tokens(connection_id=user_data["connectionId"], provider_config_key=user_data["providerConfigKey"])
        
        self.user_data = user_data
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]
        pass
