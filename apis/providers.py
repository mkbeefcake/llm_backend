import requests
from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.responses import RedirectResponse

from core.bot.autobot import autobot
from core.pipeline.products import products_pipeline
from core.utils.message import MessageErr, MessageOK
from db.cruds.users import get_user_data, get_user_providers, update_user
from db.schemas.users import UsersSchema
from providers.bridge import bridge

from .users import User, get_current_user

router = APIRouter()


@router.get("/get_my_providers")
async def get_my_providers(curr_user: User = Depends(get_current_user)):
    try:
        user_id = curr_user["uid"]
        my_providers = get_user_providers(id=user_id)
        all_providers = bridge.get_all_providers()
        status_autobot = autobot.status_my_auto_bot(curr_user)
        return MessageOK(
            data={
                "my_providers": my_providers,
                "providers": all_providers,
                "status_autobot": status_autobot,
            }
        )
    except Exception as e:
        return MessageErr(reason=str(e))


@router.get("/get_providers")
async def get_providers(curr_user: User = Depends(get_current_user)):
    try:
        return MessageOK(data=bridge.get_all_providers())
    except Exception as e:
        return MessageErr(reason=str(e))


@router.get("/google_auth")
async def google_auth(request: Request):
    try:
        return await bridge.get_access_token("gmailprovider", request)
    except Exception as e:
        return MessageErr(reason=str(e))


@router.get("/link_provider")
async def link_Provider(
    provider_name: str = "gmailprovider",
    redirect_url: str = "http://localhost:3000/callback/oauth",
    request: Request = None,
):
    try:
        return await bridge.link_provider(provider_name, redirect_url, request)
    except Exception as e:
        return MessageErr(reason=str(e))


@router.get("/unlink_provider")
async def unlink_Provider(
    provider_name: str = "gmailprovider",
    identifier_name: str = "john doe",
    request: Request = None,
    curr_user: User = Depends(get_current_user),
):
    try:
        await bridge.disconnect(provider_name, identifier_name, request)
        return MessageOK(
            data=update_user(
                user=UsersSchema(id=curr_user["uid"], email=curr_user["email"]),
                provider_name=provider_name,
                key=identifier_name,
                content="",
            )
        )
    except Exception as e:
        return MessageErr(reason=str(e))


@router.post("/update_provider_info")
async def update_provider_info(
    provider_name: str = "gmailprovider",
    identifier_name: str = "john doe",
    social_info: str = "",
    curr_user: User = Depends(get_current_user),
):
    try:
        user_id = curr_user["uid"]
        result = update_user(
            user=UsersSchema(id=user_id, email=curr_user["email"]),
            provider_name=provider_name,
            key=identifier_name,
            content=social_info,
        )

        user_data = get_user_data(user_id)
        bridge.update_provider_info(
            user_id,
            provider_name,
            identifier_name,
            user_data[provider_name][identifier_name],
        )

        # await products_pipeline.fetch_purchased_products_for_one(
        #     user_id,
        #     provider_name,
        #     identifier_name,
        #     user_data=user_data[provider_name][identifier_name],
        # )
        response = requests.post(
            f"https://chat-automation-387710-purchased-yix5m2x4pq-uc.a.run.app/products/fetch_purchased_products_for_one?user_id={user_id}&provider_name={provider_name}&identifier_name={identifier_name}"
        )
        response_json = response.json()

        # await products_pipeline.fetch_all_products_for_one(
        #     user_id,
        #     provider_name,
        #     identifier_name,
        #     user_data=user_data[provider_name][identifier_name],
        # )
        response = requests.post(
            f"https://chat-automation-387710-products-yix5m2x4pq-uc.a.run.app/products/fetch_all_products_for_one?user_id={user_id}&provider_name={provider_name}&identifier_name={identifier_name}"
        )
        response_json = response.json()

        return MessageOK(data=result)
    except Exception as e:
        return MessageErr(reason=str(e))
