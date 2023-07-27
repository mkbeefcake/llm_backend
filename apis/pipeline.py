import os

from fastapi import APIRouter

from core.pipeline.chathistories import chathistory_pipeline
from core.pipeline.products import products_pipeline
from core.utils.message import MessageErr, MessageOK
from db.cruds.users import get_user_data

router = APIRouter()

BACKEND_TYPE = os.getenv("BACKEND_TYPE")

if BACKEND_TYPE is None or BACKEND_TYPE == "CHATHISTORY":

    @router.post(
        "/get_chat_history_for_one",
        summary="Get chat history for the account",
        description="This endpoint is used to get chat history for the account which specified by provider and identifier name.<br>"
        "It tries to get last 1000 messages for all users between the account.<br><br>"
        "<i>user_id</i> : indicates the end-user's id in the database<br>"
        "<i>provider_name</i> : indicates the provider name such as 'gmailprovider' or 'replicateprovider'<br>"
        "<i>identifier_name</i> : indicates the account name",
    )
    async def get_chat_history_for_one(user_id, provider_name, identifier_name):
        try:
            user_data = get_user_data(user_id)
            chathistory_pipeline.fetch_history_for_one(
                user_id,
                provider_name,
                identifier_name,
                user_data=user_data[provider_name][identifier_name],
            )

            return MessageOK(
                data={
                    "message": "User started import_chat_history_for_one successfully"
                }
            )
        except Exception as e:
            return MessageErr(reason=str(e))

    @router.post(
        "/stop_chat_history_for_one",
        summary="Stop the chat history thread for the account.",
        description="This endpoint is used to stop chat history thread for the account.<br><br>"
        "<i>user_id</i> : indicates the end-user's id in the database<br>"
        "<i>provider_name</i> : indicates the provider name such as 'gmailprovider' or 'replicateprovider'<br>"
        "<i>identifier_name</i> : indicates the account name",
    )
    async def stop_chat_history_for_one(user_id, provider_name, identifier_name):
        try:
            await chathistory_pipeline.stop_history_task(
                uid=user_id,
                provider_name=provider_name,
                identifier_name=identifier_name,
            )
            return MessageOK(
                data={"message": "User stopped chat_history-bot successfully"}
            )
        except Exception as e:
            return MessageErr(reason=str(e))


if BACKEND_TYPE is None or BACKEND_TYPE == "PURCHASED":

    @router.post(
        "/fetch_purchased_products",
        summary="Get all purchased products list for all accounts",
        description="This endpoint is used to get all purchased products list for all accounts in the system",
    )
    async def fetch_purchased_products():
        try:
            products_pipeline.fetch_purchased_products()
            return MessageOK(
                data={"message": "User started import_purchased_products successfully"}
            )
        except Exception as e:
            return MessageErr(reason=str(e))

    @router.post(
        "/fetch_purchased_products_for_one",
        summary="Get all purchased products for one account",
        description="This endpoint is used to get all purchased products for one account which specified by provider and identifier name.<br><br>"
        "<i>user_id</i> : indicates the end-user's id in the database<br>"
        "<i>provider_name</i> : indicates the provider name such as 'gmailprovider' or 'replicateprovider'<br>"
        "<i>identifier_name</i> : indicates the account name",
    )
    async def fetch_purchased_products_for_one(user_id, provider_name, identifier_name):
        try:
            user_data = get_user_data(user_id)
            await products_pipeline.fetch_purchased_products_for_one(
                user_id,
                provider_name,
                identifier_name,
                user_data=user_data[provider_name][identifier_name],
            )

            return MessageOK(
                data={
                    "message": "User started import_purchased_products_for_one successfully"
                }
            )
        except Exception as e:
            return MessageErr(reason=str(e))

    @router.post(
        "/stop_purchased_products_for_one",
        summary="Stop purchased products thread for one account",
        description="This endpoint is used to stop the thread fetching purchased products for one account which specified by provider and identifier name.<br><br>"
        "<i>user_id</i> : indicates the end-user's id in the database<br>"
        "<i>provider_name</i> : indicates the provider name such as 'gmailprovider' or 'replicateprovider'<br>"
        "<i>identifier_name</i> : indicates the account name",
    )
    async def stop_purchased_products_for_one(user_id, provider_name, identifier_name):
        try:
            await products_pipeline.stop_purchased_products_task(
                uid=user_id,
                provider_name=provider_name,
                identifier_name=identifier_name,
            )
            return MessageOK(
                data={"message": "User stopped purchased-bot successfully"}
            )
        except Exception as e:
            return MessageErr(reason=str(e))


if BACKEND_TYPE is None or BACKEND_TYPE == "PRODUCT":

    @router.post(
        "/fetch_all_products",
        summary="Get all products for all accounts",
        description="This endpoint is used to get all products list for all accounts in the system",
    )
    async def fetch_all_products():
        try:
            products_pipeline.fetch_all_products()
            return MessageOK(
                data={"message": "User started import_all_products successfully"}
            )
        except Exception as e:
            return MessageErr(reason=str(e))

    @router.post(
        "/fetch_all_products_for_one",
        summary="Get all products for one account",
        description="This endpoint is used to get all products for one account which specified by provider and identifier name.<br><br>"
        "<i>user_id</i> : indicates the end-user's id in the database<br>"
        "<i>provider_name</i> : indicates the provider name such as 'gmailprovider' or 'replicateprovider'<br>"
        "<i>identifier_name</i> : indicates the account name",
    )
    async def fetch_all_products_for_one(user_id, provider_name, identifier_name):
        try:
            user_data = get_user_data(user_id)
            await products_pipeline.fetch_all_products_for_one(
                user_id,
                provider_name,
                identifier_name,
                user_data=user_data[provider_name][identifier_name],
            )

            return MessageOK(
                data={
                    "message": "User started import_all_products_for_one successfully"
                }
            )
        except Exception as e:
            return MessageErr(reason=str(e))

    @router.post(
        "/stop_all_products_for_one",
        summary="Stop products thread for one account",
        description="This endpoint is used to stop the thred fetching all products for one account which specified by provider and identifier name.<br><br>"
        "<i>user_id</i> : indicates the end-user's id in the database<br>"
        "<i>provider_name</i> : indicates the provider name such as 'gmailprovider' or 'replicateprovider'<br>"
        "<i>identifier_name</i> : indicates the account name",
    )
    async def stop_all_products_for_one(user_id, provider_name, identifier_name):
        try:
            await products_pipeline.stop_all_products_task(
                uid=user_id,
                provider_name=provider_name,
                identifier_name=identifier_name,
            )
            return MessageOK(
                data={"message": "User stopped all-product-bot successfully"}
            )
        except Exception as e:
            return MessageErr(reason=str(e))
