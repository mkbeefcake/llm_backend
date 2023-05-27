from core.bot.base import BaseProviderBot
from core.timestamp import get_current_timestamp
from providers.bridge import bridge
from google.auth.exceptions import RefreshError

PROVIDER_NAME = "GMailProvider"

class GMailProviderBot(BaseProviderBot):

    def __init__(self):
        self.sync_time = -1

    async def start(self, user_data: any):        
        try:
            access_token = user_data['access_token']
            # refresh_token = user_data['refresh_token']

            last_message = bridge.get_last_message(provider_name=PROVIDER_NAME, access_token=access_token, option="")
            print(f"last_message: {last_message['snippet']}")

        except NotImplementedError:
            print(f'[GMailProviderBot] Error: GMailProvider is Not implemented')
            pass
        except RefreshError as e:
            print(f'[GMailProviderBot] Error: {str(e)}, rescheduled to next time after get access_token')
            pass
        except Exception as e:
            print(f'[GMailProviderBot] Error: {str(e)}')
            pass

        self.sync_time = get_current_timestamp()
        pass