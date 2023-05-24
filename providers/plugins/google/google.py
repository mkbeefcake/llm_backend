import sys
from providers.base import BaseProvider

#
# get messages
#

# import requests
#  # Set the API endpoint URL
# api_url = 'https://chat.googleapis.com/v1/spaces/SPACE_ID/messages'
#  # Set the headers with the access token
# headers = {
#     'Authorization': 'Bearer ACCESS_TOKEN',
#     'Content-Type': 'application/json; charset=UTF-8'
# }
#  # Make a GET request to retrieve the messages
# response = requests.get(api_url, headers=headers)
#  # Extract the messages from the response JSON
# messages = response.json()['messages']

class Google(BaseProvider):

    def get_access_token(self, email: str, password: str, option: any) -> str:
        print("[%s]: get_access_token: %s | %s, %s" % (self.plugin_name, email, password, option), file=sys.stdout)

    def get_profile(self, access_token: str, option: any):
        print("[%s]: get_profile: %s, %s" % (self.plugin_name, access_token, option), file=sys.stdout)
    
    def get_last_message(self, access_token: str, option: any):
        print("[%s]: get_last_message: %s, %s" % (self.plugin_name, access_token, option), file=sys.stdout)

    def get_messages(self, access_token: str, from_when: str, option: any):
        print("[%s]: get_messages: %s %s, %s" % (self.plugin_name, access_token, from_when, option), file=sys.stdout)
     
    def disconnect(self, access_token: str, option: any):
        print("[%s]: disconnect: %s, %s" % (self.plugin_name, access_token, option), file=sys.stdout)

    pass