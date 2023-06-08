from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.responses import RedirectResponse

from core.message import MessageErr, MessageOK
from core.task import task_manager
from db.cruds.users import get_user_providers, update_user
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
        status_autobot = task_manager.status_my_auto_bot(curr_user)
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
        bridge.disconnect(provider_name, request)
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
        return MessageOK(
            data=update_user(
                user=UsersSchema(id=curr_user["uid"], email=curr_user["email"]),
                provider_name=provider_name,
                key=identifier_name,
                content=social_info,
            )
        )
    except Exception as e:
        return MessageErr(reason=str(e))


@router.get("/get_last_message")
async def get_last_message(
    provider_name: str = "gmailprovider",
    access_token: str = "",
    option: str = "",
    curr_user: User = Depends(get_current_user),
):
    try:
        result = bridge.get_last_message(provider_name, access_token, option=option)
        return MessageOK(data={"message": result})
    except Exception as e:
        return MessageErr(reason=str(e))


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
        return MessageOK(data={"message": result})
    except Exception as e:
        return MessageErr(reason=str(e))


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
        return MessageOK(data={"message": result})
    except Exception as e:
        return MessageErr(reason=str(e))


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
        return MessageOK(data={"message": result})
    except Exception as e:
        return MessageErr(reason=str(e))
