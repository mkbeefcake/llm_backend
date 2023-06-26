from fastapi import APIRouter, Depends

from core.utils.message import MessageErr, MessageOK
from providers.bridge import bridge

from .users import User, get_current_user

router = APIRouter()


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
