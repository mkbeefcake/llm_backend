from fastapi import FastAPI, Depends, HTTPException, Security, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, SecretStr
from core.firebase import authenticate_user, decode_access_token, create_user
from helpers.forms import BasicAuthenticationForm
from core.error import Error
from core.task import task_manager

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
    result = authenticate_user(form_data.username, form_data.password)
    if type(result) is Error:
        raise HTTPException(status_code=400, detail=result.description)
    
    return {"access_token": result, "token_type": "bearer"}

@router.post("/signup")
async def signup(form_data: BasicAuthenticationForm = Depends()):
    user = create_user(form_data.email, form_data.password)
    return {"message": "User created successfully"}

@router.post("/start_auto_bot")
async def start_auto_bot(interval_seconds: int = 300, curr_user: User = Depends(get_current_user)):
    task_manager.start_auto_bot(user=curr_user, interval=interval_seconds)
    return {"message": "User started auto-bot successfully"}

@router.post("/stop_auto_bot")
async def stop_auto_bot(curr_user: User = Depends(get_current_user)):
    task_manager.stop_auto_bot(user=curr_user)
    return {"message": "User stopped auto-bot successfully"}

@router.post("/status_auto_bot")
async def status_auto_bot(curr_user: User = Depends(get_current_user)):
    result = task_manager.status_auto_bot(user=curr_user)
    return {"message": { "status" : result }}