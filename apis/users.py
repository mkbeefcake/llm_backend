from fastapi import APIRouter, Depends, FastAPI, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, SecretStr

from core.firebase import authenticate_user, create_user, decode_access_token
from core.message import MessageErr, MessageOK
from core.task import task_manager
from helpers.forms import BasicAuthenticationForm

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")


class User(BaseModel):
    email: str


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        user = decode_access_token(token)
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="User unauthorized")


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    try:
        email = current_user["email"]
        return MessageOK(data={"email": email})
    except Exception as e:
        return MessageErr(reason=str(e))


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        result = authenticate_user(form_data.username, form_data.password)
        return {"access_token": result, "token_type": "bearer"}
    except Exception as e:
        return MessageErr(reason=str(e))


@router.post("/signup")
async def signup(form_data: BasicAuthenticationForm = Depends()):
    try:
        user = create_user(form_data.email, form_data.password)
        return MessageOK(data={"message": "User created successfully"})
    except Exception as e:
        return MessageErr(reason=str(e))


@router.post("/start_auto_bot")
async def start_auto_bot(
    provider_name: str = "gmailprovider",
    interval_seconds: int = 300,
    curr_user: User = Depends(get_current_user),
):
    try:
        task_manager.start_auto_bot(
            user=curr_user, provider_name=provider_name, interval=interval_seconds
        )
        return MessageOK(data={"message": "User started auto-bot successfully"})
    except Exception as e:
        return MessageErr(reason=str(e))


@router.post("/stop_auto_bot")
async def stop_auto_bot(
    provider_name: str = "gmailprovider", curr_user: User = Depends(get_current_user)
):
    try:
        task_manager.stop_auto_bot(user=curr_user, provider_name=provider_name)
        return MessageOK(data={"message": "User stopped auto-bot successfully"})
    except Exception as e:
        return MessageErr(reason=str(e))


@router.post("/status_auto_bot")
async def status_auto_bot(
    provider_name: str = "gmailprovider", curr_user: User = Depends(get_current_user)
):
    try:
        result = task_manager.status_auto_bot(
            user=curr_user, provider_name=provider_name
        )
        return MessageOK(data={"message": {"status": result}})
    except Exception as e:
        return MessageErr(reason=str(e))
