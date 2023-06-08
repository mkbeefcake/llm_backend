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
