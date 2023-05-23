from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    passwd: str