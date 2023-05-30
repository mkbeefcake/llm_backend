from google.auth.exceptions import RefreshError

from core.bot.base import BaseProviderBot
from core.timestamp import get_current_timestamp
from providers.bridge import bridge
from services.service import ai_service

PROVIDER_NAME = "GMailProvider"
MAX_MAIL_COUNT = 10


class GMailProviderBot(BaseProviderBot):
    def __init__(self):
        self.sync_time = -1
        self.access_token = None
        self.refresh_token = None

    async def start(self, user_data: any):
        try:
            if self.access_token is None:
                self.access_token = user_data["access_token"]

            if self.refresh_token is None:
                self.refresh_token = user_data["refresh_token"]

            if self.sync_time == -1:
                last_message = bridge.get_last_message(
                    provider_name=PROVIDER_NAME,
                    access_token=self.access_token,
                    option="",
                )
                ai_response = ai_service.get_response(
                    service_name="", message=last_message["snippet"], option=""
                )
                bridge.reply_to_message(
                    provider_name=PROVIDER_NAME,
                    access_token=self.access_token,
                    to=last_message["messageId"],
                    message=ai_response["message"],
                    option="",
                )
                print(
                    f"LastMessage: {last_message['snippet']}, response: {ai_response['message']}"
                )
            else:
                last_messages = bridge.get_messages(
                    provider_name=PROVIDER_NAME,
                    access_token=self.access_token,
                    from_when=self.sync_time,
                    count=MAX_MAIL_COUNT,
                    option="",
                )

                for message in last_messages["messages"]:
                    ai_response = ai_service.get_response(
                        service_name="", message=message["snippet"], option=""
                    )
                    bridge.reply_to_message(
                        provider_name=PROVIDER_NAME,
                        access_token=self.access_token,
                        to=message["messageId"],
                        message=ai_response["message"],
                        option="",
                    )
                    print(
                        f"Message: {message['snippet']}, response: {ai_response['message']}"
                    )

            self.sync_time = get_current_timestamp()
        except NotImplementedError:
            print(f"[GMailProviderBot] Error: GMailProvider is Not implemented")
            pass
        except RefreshError as e:
            self.access_token = bridge.get_access_token_from_refresh_token(
                provider_name=PROVIDER_NAME, refresh_token=self.refresh_token
            )
            print(
                f"[GMailProviderBot] Error: {str(e)}, rescheduled to next time after get access_token"
            )
            pass
        except Exception as e:
            print(f"[GMailProviderBot] Error: {str(e)}")
            pass

        pass
