from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.responses import RedirectResponse

from core.bot.autobot import autobot
from core.utils.message import MessageErr, MessageOK

from .users import User, get_current_user

router = APIRouter()


@router.post("/start_auto_bot")
async def start_auto_bot(
    provider_name: str = "gmailprovider",
    identifier_name: str = "john doe",
    interval_seconds: int = 25,
    curr_user: User = Depends(get_current_user),
):
    try:
        autobot.start_auto_bot(
            user=curr_user,
            provider_name=provider_name,
            identifier_name=identifier_name,
            interval=interval_seconds,
        )
        return MessageOK(data={"message": "User started auto-bot successfully"})
    except Exception as e:
        return MessageErr(reason=str(e))


@router.post("/stop_auto_bot")
async def stop_auto_bot(
    provider_name: str = "gmailprovider",
    identifier_name: str = "john doe",
    curr_user: User = Depends(get_current_user),
):
    try:
        await autobot.stop_auto_bot(
            user=curr_user, provider_name=provider_name, identifier_name=identifier_name
        )
        return MessageOK(data={"message": "User stopped auto-bot successfully"})
    except Exception as e:
        return MessageErr(reason=str(e))


@router.post("/status_auto_bot")
async def status_auto_bot(
    provider_name: str = "gmailprovider",
    identifier_name: str = "john doe",
    curr_user: User = Depends(get_current_user),
):
    try:
        result = autobot.status_auto_bot(
            user=curr_user, provider_name=provider_name, identifier_name=identifier_name
        )
        return MessageOK(data={"message": {"status": result}})
    except Exception as e:
        return MessageErr(reason=str(e))
