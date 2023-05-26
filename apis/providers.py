from fastapi import FastAPI, Request, APIRouter, Depends
from providers.bridge import bridge
from .users import get_current_user, User

router = APIRouter()

@router.get("/link_social_provider")
async def linkSocialProvider(provider_name: str = "gmailprovider", request: Request = None):
    return await bridge.link_provider(provider_name, request)

@router.get("/unlink_social_provider")
async def unlinkSocialProvider(provider_name: str = "gmailprovider", curr_user: User = Depends(get_current_user), request: Request = None):
    bridge.disconnect(provider_name, request)
    return {"message": "Unlink user successfully"}

@router.get("/google_auth")
async def google_auth(request: Request):
    result = await bridge.get_access_token("gmailprovider", request)
    return {"message": result}

@router.get("get_last_message")
async def get_last_message(provider_name: str = "gmailprovider", access_token: str = "", curr_user: User = Depends(get_current_user)):
    result = bridge.get_last_message(provider_name, access_token, option="")
    return {"message": result}