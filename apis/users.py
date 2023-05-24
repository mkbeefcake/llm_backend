from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from core.firebase import authenticate_user, decode_access_token, create_user
from helpers.forms import BasicAuthenticationForm
from providers.provider import send_message

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

class User(BaseModel):
    email: str

def get_current_user(token: str = Depends(oauth2_scheme)):
    user = decode_access_token(token)
    return user

@router.get("/me", response_model=User)
async def me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):  
    access_token = authenticate_user(form_data.username, form_data.password)
    if not access_token:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    send_message("DummyProvider", access_token, to="*", msg="hello world")

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/signup")
async def signup(form_data: BasicAuthenticationForm = Depends()):
    user = create_user(form_data.username, form_data.password)
    return {"message": "User created successfully"}