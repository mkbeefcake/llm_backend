from fastapi import APIRouter
from providers.provider import send_message

router = APIRouter()

@router.post("/send_message_to")
async def send_message_to(provider_name: str, social_token: str, to: str, message: str):  
    send_message(provider_name, access_token=social_token, to=to, msg=message)
    return {"message": "Message sent successfully"}
