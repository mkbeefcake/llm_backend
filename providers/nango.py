import os
import requests
import json

from pydantic import BaseModel
from providers.base import BaseProvider

NANGO_SECRET_KEY = os.getenv("NANGO_SECRET_KEY")

class NangoResponseResults(BaseModel):
    added: int
    updated: int
    deleted: int

class NangoEventData(BaseModel):
    from_: str = "nango"  # Using 'from_' to avoid conflict with Python keyword 'from'
    type_: str = "sync"  # Using 'type_' to avoid conflict with Python keyword 'type'
    connectionId: str
    providerConfigKey: str
    syncName: str
    model: str
    responseResults: NangoResponseResults
    syncType: str
    modifiedAfter: str
    queryTimeStamp: str

    class Config:
        # Optional field to allow additional fields not defined in the model
        extra = "allow"

class NangoProvider(BaseProvider):

    def get_credential_tokens(self, connection_id, provider_config_key):

        url = f'https://api.nango.dev/connection/{connection_id}'

        headers = {"Authorization": f"Bearer {NANGO_SECRET_KEY}"}
        query = {"provider_config_key": provider_config_key, "refresh_token": "true"}
        response = requests.request("GET", url, headers=headers, params=query)
        
        if response.ok:
            result = json.loads(response.text)
            return {
                "access_token": result["credentials"]["access_token"], 
                "refresh_token": result["credentials"]["refresh_token"]
            }
        
        return {}

    def delete_connection(self, connection_id, provider_config_key):
        url = f'https://api.nango.dev/connection/{connection_id}'
        headers = {"Authorization": f"Bearer {NANGO_SECRET_KEY}"}
        query = {"provider_config_key": provider_config_key}
        response = requests.request("DELETE", url, headers=headers, params=query)
