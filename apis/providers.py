from fastapi import FastAPI, Request, APIRouter, Depends
from fastapi.responses import RedirectResponse
from providers.bridge import bridge
from .users import get_current_user, User
from db.cruds.users import update_user
from db.schemas.users import UsersSchema

router = APIRouter()

@router.get("/google_auth")
async def google_auth(request: Request):
    result = await bridge.get_access_token("gmailprovider", request)
    return {"message": "User logged successfully", "data": result}    

@router.get("/link_social_provider")
async def linkSocialProvider(provider_name: str = "gmailprovider", request: Request = None):
    return await bridge.link_provider(provider_name, request)

@router.get("/unlink_social_provider")
async def unlinkSocialProvider(provider_name: str = "gmailprovider", 
                               request: Request = None, 
                               curr_user: User = Depends(get_current_user)):
    bridge.disconnect(provider_name, request)
    return {"message": "Unlink user successfully"}

@router.post("/save_social_info_to_user")
async def save_social_info_to_user(provider_name: str = "gmailprovider",
                           social_info: str = "",
                           curr_user: User = Depends(get_current_user)):
    return update_user(user=UsersSchema(id=curr_user["uid"], email=curr_user["email"]), 
                       key=provider_name, 
                       content=social_info)

@router.get("/get_last_message")
async def get_last_message(provider_name: str = "gmailprovider", 
                           access_token: str = "",                            
                           option: str = "",
                           curr_user: User = Depends(get_current_user)):
    result = bridge.get_last_message(provider_name, access_token, option=option)
    return {"message": result}

@router.get("/get_messages")
async def get_messages(provider_name: str = "gmailprovider", 
                       access_token: str = "", 
                       from_what: str = "is:unread",
                       count: int = 1,
                       option: str = "",
                       curr_user: User = Depends(get_current_user)):
    result = bridge.get_messages(provider_name, access_token, from_what, count, option)
    return {"message": result}

@router.post("/reply_to_message")
async def reply_to_message(provider_name: str = "gmailprovider",
                           access_token: str = "",
                           to: str = "",
                           message: str = "",
                           option: str = "",
                           curr_user: User = Depends(get_current_user)):
    result = bridge.reply_to_message(provider_name, access_token, to, message, option)
    return {"message": result}