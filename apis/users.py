from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
import datetime
from passlib.hash import bcrypt
from core.security import create_access_token, decode_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

fake_users_database = {
    "mkblockchaindev" : {
        "username" : "mkblockchaindev",
        "passwd" : bcrypt.hash("testtest"),
        "email" : "mkblockchaindev@outlook.com"
    }
}

class User(BaseModel):
    username: str
    email: Optional[str] = None

# authenticate user with fake user database
def authenticate_user(username: str, password: str): 
    user = fake_users_database.get(username)
    if not user:
        return None
    if not bcrypt.verify(password, user["passwd"]):
        return None
    return user

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    username: str = payload.get("sub")
    
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = fake_users_database.get(username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
        
    return user

@router.get("/me", response_model=User)
async def me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):    
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    print('user', user)

    access_token_expires = datetime.timedelta(minutes=30)
    access_token = create_access_token(data={"sub":user["username"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

