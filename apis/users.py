from fastapi import APIRouter, Depends, FastAPI, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, SecretStr

from core.utils.message import MessageErr, MessageOK
from db.firebase import authenticate_user, create_user, decode_access_token
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


@router.get(
    "/me",
    summary="Get end-user's info",
    description="Get end-user's information after logged in, returns only email at this moment.",
)
async def me(current_user: User = Depends(get_current_user)):
    try:
        email = current_user["email"]
        return MessageOK(data={"email": email})
    except Exception as e:
        return MessageErr(reason=str(e))


@router.post(
    "/token",
    summary="Sign in end-user",
    description="Sign in the end-user by using email/password.<br><br>"
    "<i>username</i> : indicates the end-user's email address<br>"
    "<i>password</i> : indicates the end-user's password<br>",
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        result = authenticate_user(form_data.username, form_data.password)
        return {"access_token": result, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=401, detail="User unauthorized")
        # return MessageErr(reason=str(e))


@router.post(
    "/loginWithToken",
    summary="Sign in end-user with 3rd party token",
    description="Sign in the end-user by using OAuth2 token, support gmail sign-in at this moment.<br><br>"
    "<i>token</i> : indicates the access_token generated by OAuth2 provider",
)
async def loginWithToken(token: str):
    try:
        result = decode_access_token(token)
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        return MessageErr(reason=str(e))


@router.post(
    "/signup",
    summary="Sign up end-user",
    description="Sign up the end-user by using email/password.<br><br>"
    "<i>email</i> : indicates new end-user's email address<br>"
    "<i>password</i> : indicates new end-user's password",
)
async def signup(form_data: BasicAuthenticationForm = Depends()):
    try:
        user = create_user(form_data.email, form_data.password)
        return MessageOK(data={"message": "User created successfully"})
    except Exception as e:
        return MessageErr(reason=str(e))
