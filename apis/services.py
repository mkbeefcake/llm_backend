from fastapi import APIRouter, Body
from providers.bridge import bridge

router = APIRouter()

@router.post("/get_access_token")
async def get_access_token(provider_name: str = "gmailprovider", email: str = "test@gmail.com", password: str = "testtest", option: str = ""):  
    result = bridge.get_access_token(provider_name, email, password, option)
    return {
        "success": True,
        "data" : result
    }

@router.post("/get_profile")
async def get_profile(provider_name: str = "gmailprovider", access_token: str = "XXXYYYZZZ", option: str = ""):  
    result = bridge.get_profile(provider_name, access_token, option)
    return {
        "success": True,
        "data" : result
    }

@router.post("/get_last_message")
async def get_last_message(provider_name: str = "gmailprovider", access_token: str = "XXXYYYZZZ", option: str = ""):  
    result = bridge.get_last_message(provider_name, access_token, option)
    return {
        "success": True,
        "data" : result
    }

@router.post("/get_messages")
async def get_messages(provider_name: str = "gmailprovider", access_token: str = "XXXYYYZZZ", from_when: str = "", option: str = ""):  
    result = bridge.get_messages(provider_name, access_token, from_when, option)
    return {
        "success": True,
        "data" : result
    }

@router.post("/send_message")
async def send_message(provider_name: str = "gmailprovider", access_token: str = "", to: str = "", msg: str = "", option: str = ""):  
    result = bridge.send_message(provider_name, access_token, to, msg, option)
    return {
        "success": True,
        "data": result
    }


@router.post("/get_profile")
async def get_profile(provider_name: str = "gmailprovider", access_token: str = "XXXYYYZZZ", option: str = ""):  
    result = bridge.get_profile(provider_name, access_token, option)
    return {
        "success": True,
        "data" : result
    }
