from fastapi import FastAPI, Request, APIRouter, Depends
from fastapi.responses import RedirectResponse
from providers.bridge import bridge
from .users import get_current_user, User
from db.cruds.users import update_user
from db.schemas.users import UsersSchema

router = APIRouter()


@router.get("/google_auth")
async def google_auth(request: Request):
    try:
        result = await bridge.get_access_token("gmailprovider", request)
        return {"message": "User logged successfully", "data": result}
    except Exception as e:
        return {"error": str(e)}


@router.get("/link_provider")
async def link_Provider(provider_name: str = "gmailprovider", request: Request = None):
    try:
        return await bridge.link_provider(provider_name, request)
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
