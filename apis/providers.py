from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.responses import RedirectResponse

from db.cruds.users import update_user
from db.schemas.users import UsersSchema
from providers.bridge import bridge
from providers.provider import provider

from .users import User, get_current_user

router = APIRouter()


@router.get("/get_my_providers")
async def get_my_providers(curr_user: User = Depends(get_current_user)):
    try:
        return provider.get_my_providers(user=curr_user)
    except Exception as e:
        return {"error": str(e)}


@router.get("/get_providers")
async def get_providers(curr_user: User = Depends(get_current_user)):
    try:
        return provider.get_all_providers()
    except Exception as e:
        return {"error": str(e)}


# @router.post("/register_provider")
# async def register_provider(
#     provider_name: str = "gmailprovider",
#     provider_description: str = "Gmail Provider",
#     provider_icon_url: str = "",
#     curr_user: User = Depends(get_current_user),
# ):
#     try:
#         return provider.create_provider(
#             provider_name, provider_description, provider_icon_url
#         )
#     except Exception as e:
#         return {"error": str(e)}


@router.get("/google_auth")
async def google_auth(request: Request):
    try:
        return await bridge.get_access_token("gmailprovider", request)
    except Exception as e:
        return {"error": str(e)}


@router.get("/link_provider")
async def link_Provider(
    provider_name: str = "gmailprovider",
    redirect_url: str = "http://localhost:3000/callback/oauth",
    request: Request = None,
):
    try:
        return await bridge.link_provider(provider_name, redirect_url, request)
    except Exception as e:
        return {"error": str(e)}


@router.get("/unlink_provider")
async def unlink_Provider(
    provider_name: str = "gmailprovider",
    request: Request = None,
    curr_user: User = Depends(get_current_user),
):
    try:
        bridge.disconnect(provider_name, request)
        return update_user(
            user=UsersSchema(id=curr_user["uid"], email=curr_user["email"]),
            key=provider_name,
            content="",
        )
        return {"message": "Unlink user successfully"}
    except Exception as e:
        return {"error": str(e)}


@router.post("/update_provider_info")
async def update_provider_info(
    provider_name: str = "gmailprovider",
    social_info: str = "",
    curr_user: User = Depends(get_current_user),
):
    try:
        return update_user(
            user=UsersSchema(id=curr_user["uid"], email=curr_user["email"]),
            key=provider_name,
            content=social_info,
        )
    except Exception as e:
        return {"error": str(e)}


@router.get("/get_last_message")
async def get_last_message(
    provider_name: str = "gmailprovider",
    access_token: str = "",
    option: str = "",
    curr_user: User = Depends(get_current_user),
):
    try:
        result = bridge.get_last_message(provider_name, access_token, option=option)
        return {"message": result}
    except Exception as e:
        return {"err": str(e)}


@router.get("/get_full_messages")
async def get_full_message(
    provider_name: str = "gmailprovider",
    access_token: str = "",
    of_what: str = "message_id",
    option: str = "",
    curr_user: User = Depends(get_current_user),
):
    try:
        result = bridge.get_full_messages(provider_name, access_token, of_what, option)
        return {"message": result}
    except Exception as e:
        return {"err": str(e)}


@router.get("/get_messages")
async def get_messages(
    provider_name: str = "gmailprovider",
    access_token: str = "",
    from_when: str = "2023/05/27 03:00:00",
    count: int = 1,
    option: str = "",
    curr_user: User = Depends(get_current_user),
):
    try:
        result = bridge.get_messages(
            provider_name, access_token, from_when, count, option
        )
        return {"message": result}
    except Exception as e:
        return {"err": str(e)}


@router.post("/reply_to_message")
async def reply_to_message(
    provider_name: str = "gmailprovider",
    access_token: str = "",
    to: str = "",
    message: str = "",
    option: str = "",
    curr_user: User = Depends(get_current_user),
):
    try:
        result = bridge.reply_to_message(
            provider_name, access_token, to, message, option
        )
        return {"message": result}
    except Exception as e:
        return {"err": str(e)}
