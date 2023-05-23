from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from core.firebase import authenticate_user, decode_access_token

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
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token = user['idToken']
    return {"access_token": access_token, "token_type": "bearer"}

