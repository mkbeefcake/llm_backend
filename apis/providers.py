from fastapi import FastAPI, Request, APIRouter
from providers.bridge import bridge

router = APIRouter()

@router.get("/link_social_provider")
async def linkSocialProvider(provider_name: str = "gmailprovider", request: Request = None):
    return await bridge.link_provider(provider_name, request)

@router.get("/unlink_social_provider")
async def unlinkSocialProvider(provider_name: str = "gmailprovider", request: Request = None):
    bridge.disconnect(provider_name, request)
    return {"message": "Unlink user successfully"}

@router.get("/google_auth")
async def google_auth(request: Request):
    result = await bridge.get_access_token("gmailprovider", request)
    return {"message": result}
