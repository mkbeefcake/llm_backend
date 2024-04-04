from pathlib import Path
import base64
import json
import sys

from email.mime.text import MIMEText
from pathlib import Path
from urllib.parse import urlencode
from starlette.requests import Request

from providers.nango import NangoProvider
from services.cpa.ads import google_ads_cpa

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

    async def get_access_token_from_refresh_token(self, refresh_token: str) -> str:
        if self.user_data:
            url = f'https://api.nango.dev/connection/{self.user_data["connectionId"]}'

            headers = {"Authorization": f"Bearer {NANGO_SECRET_KEY}"}
            query = {"provider_config_key": self.user_data["providerConfigKey"], "refresh_token": "true"}
            response = req.request("GET", url, headers=headers, params=query)
            
            if response.ok:
                result = json.loads(response.text)
                return result["credentials"]["access_token"]

        return ""

    def update_provider_info(self, user_data: any, option: any = None):
        print(f"user_data: {user_data}")
        tokens = self.get_credential_tokens(connection_id=user_data["connectionId"], provider_config_key=user_data["providerConfigKey"])
        
        self.user_data = user_data
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]
        pass

    def get_last_message(self, access_token: str, option: any):
        
        pass

    def get_messages(self, access_token: str, from_when: str, count: int, option: any):
        pass

    async def start_autobot(self, user_data: any, option: any):
        try:
            if self.access_token is None:
                self.update_provider_info(user_data=user_data)

            if self.sync_time == -1:
                last_message = self.get_last_message(
                    access_token=self.access_token,
                    option="",
                )
                google_ads_cpa.analyze_cpa_data(last_message)                
                BackLog.info(
                    instance=self,
                    message=f"LastMessage: {last_message['snippet']}, response: {ai_response}",
                )
            else:
                last_messages = self.get_messages(
                    access_token=self.access_token,
                    from_when=self.sync_time,
                    count=MAX_MESSAGES_COUNT,
                    option="",
                )

                for message in last_messages["messages"]:
                    google_ads_cpa.analyze_cpa_data(last_message)                
                    BackLog.info(
                        instance=self,
                        message=f"Message: {message['snippet']}, response: {ai_response}",
                    )

            self.sync_time = get_current_timestamp()
        except NotImplementedError:
            BackLog.info(
                instance=self, message=f"Error: GoogleAdsProvider is Not implemented"
            )
            pass
        except RefreshError as e:
            self.access_token = await self.get_access_token_from_refresh_token(
                refresh_token=self.refresh_token
            )
            BackLog.info(
                instance=self,
                message=f"access_token is expired, rescheduled it next time after regenerate access_token",
            )
            pass
        except Exception as e:
            BackLog.exception(instance=self, message=f"Exception occurred {str(e)}")
            pass

        pass
