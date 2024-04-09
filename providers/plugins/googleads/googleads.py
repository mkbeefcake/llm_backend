from pathlib import Path
import base64
import json
import sys
import os
import requests as req

from dotenv import load_dotenv
from email.mime.text import MIMEText
from pathlib import Path
from urllib.parse import urlencode
from starlette.requests import Request
from google.ads.googleads.client import GoogleAdsClient
from google.auth.exceptions import RefreshError
from core.utils.log import BackLog
from google.oauth2.credentials import Credentials
from core.utils.timestamp import get_current_timestamp

from providers.nango import NangoProvider, NANGO_SECRET_KEY
from services.cpa.ads import google_ads_cpa

load_dotenv()
GOOGLEADS_CLIENT_ID = os.environ.get("GOOGLEADS_CLIENT_ID")
GOOGLEADS_CLIENT_SECRET = os.environ.get("GOOGLEADS_CLIENT_SECRET")
GOOGLEADS_DEVELOPER_TOKEN = os.environ.get("GOOGLEADS_DEVELOPER_TOKEN")

SCOPES = [
    "https://www.googleapis.com/auth/adwords",
]

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

    def print_accounts_hierarchy(
        self, googleads_service, customer_client, customer_ids_to_child_accounts, depth
    ):
        """Prints the specified account's hierarchy using recursion.

        Args:
        customer_client: The customer client whose info will be printed; its
        child accounts will be processed if it's a manager.
        customer_ids_to_child_accounts: A dictionary mapping customer IDs to
        child accounts.
        depth: The current integer depth we are printing from in the account
        hierarchy.
        """
        if depth == 0:
            print("Customer ID (Descriptive Name, Currency Code, Time Zone)")

        customer_id = customer_client.id
        print("-" * (depth * 2), end="")
        print(
            f"{customer_id} ({customer_client.descriptive_name}, "
            f"{customer_client.currency_code}, "
            f"{customer_client.time_zone})"
        )

        # Recursively call this function for all child accounts of customer_client.
        if customer_id in customer_ids_to_child_accounts:
            for child_account in customer_ids_to_child_accounts[customer_id]:
                self.print_accounts_hierarchy(
                    googleads_service, child_account, customer_ids_to_child_accounts, depth + 1
                )


    def get_ads_info(self, access_token: str, option: any):
        credentials = Credentials(
            token=access_token,
            refresh_token=self.refresh_token,
            client_id=GOOGLEADS_CLIENT_ID,
            client_secret=GOOGLEADS_CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token",
            scopes=SCOPES
        )
        client = GoogleAdsClient(credentials, developer_token=GOOGLEADS_DEVELOPER_TOKEN, version='v16')
        
        # Get GoogleAdsService and CustomerService
        googleads_service = client.get_service("GoogleAdsService")
        customer_service = client.get_service("CustomerService")

        # A collection of customer IDs to handle.
        seed_customer_ids = []

        # Creates a query that retrieves all child accounts of the manager
        # specified in search calls below.
        query = """
            SELECT
            customer_client.client_customer,
            customer_client.level,
            customer_client.manager,
            customer_client.descriptive_name,
            customer_client.currency_code,
            customer_client.time_zone,
            customer_client.id
            FROM customer_client
            WHERE customer_client.level <= 1
        """

        customer_resource_names = (
            customer_service.list_accessible_customers().resource_names
        )

        for customer_resource_name in customer_resource_names:
            customer_id = googleads_service.parse_customer_path(
                customer_resource_name
            )["customer_id"]
            print(f"Customer ID: {customer_id}")
            seed_customer_ids.append(customer_id)

        # iterate all customers
        #
        for seed_customer_id in seed_customer_ids:
            # Performs a breadth-first search to build a Dictionary that maps
            # managers to their child accounts (customerIdsToChildAccounts).
            unprocessed_customer_ids = [seed_customer_id]
            customer_ids_to_child_accounts = dict()
            root_customer_client = None

            try:
                while unprocessed_customer_ids:
                    customer_id = int(unprocessed_customer_ids.pop(0))
                    response = googleads_service.search(
                        customer_id=str(customer_id), query=query
                    )

                    # Iterates over all rows in all pages to get all customer
                    # clients under the specified customer's hierarchy.
                    for googleads_row in response:
                        customer_client = googleads_row.customer_client

                        # The customer client that with level 0 is the specified
                        # customer.
                        if customer_client.level == 0:
                            if root_customer_client is None:
                                root_customer_client = customer_client
                            continue

                        # For all level-1 (direct child) accounts that are a
                        # manager account, the above query will be run against them
                        # to create a Dictionary of managers mapped to their child
                        # accounts for printing the hierarchy afterwards.
                        if customer_id not in customer_ids_to_child_accounts:
                            customer_ids_to_child_accounts[customer_id] = []

                        customer_ids_to_child_accounts[customer_id].append(
                            customer_client
                        )

                        if customer_client.manager:
                            # A customer can be managed by multiple managers, so to
                            # prevent visiting the same customer many times, we
                            # need to check if it's already in the Dictionary.
                            if (
                                customer_client.id not in customer_ids_to_child_accounts
                                and customer_client.level == 1
                            ):
                                unprocessed_customer_ids.append(customer_client.id)

                if root_customer_client is not None:
                    print(
                        "The hierarchy of customer ID "
                        f"{root_customer_client.id} is printed below:"
                    )
                    self.print_accounts_hierarchy(
                        googleads_service, root_customer_client, customer_ids_to_child_accounts, 0
                    )

                    for customer in customer_ids_to_child_accounts[root_customer_client.id]:
                        try:
                            # get all campaigns associated with customer
                            query = """
                                SELECT
                                campaign.id,
                                campaign.name
                                FROM campaign
                                ORDER BY campaign.id
                            """
                            client.login_customer_id = str(root_customer_client.id)
                            google_ads = client.get_service("GoogleAdsService")
                            response = google_ads.search(customer_id=str(customer.id), query=query)

                            for row in response:
                                print(
                                    f"Campaign with ID {row.campaign.id} and name "
                                    f'"{row.campaign.name}" was found.'
                                )
                        except Exception as e:
                            print(f"Iterating customer: {e}")
                            continue


            except Exception as e:
                print(f"Looks like production account: {e}")
                continue

        pass

    def get_messages(self, access_token: str, from_when: str, count: int, option: any):
        pass

    async def start_autobot(self, user_data: any, option: any):
        try:
            if self.access_token is None:
                self.update_provider_info(user_data=user_data)

            last_message = self.get_ads_info(
                access_token=self.access_token,
                option="",
            )
            google_ads_cpa.analyze_cpa_data(last_message)

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
