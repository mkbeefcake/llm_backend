from typing import Union

from fastapi import APIRouter, Depends

from services.service import ai_service

from .users import User, get_current_user

router = APIRouter()


@router.post("/get_ai_response")
async def get_ai_response(
    service_name: Union[str, None] = None,
    message: str = "Hi there",
    option: str = "",
    curr_user: User = Depends(get_current_user),
):
    try:
        return ai_service.get_response(service_name, message, option)
    except Exception as e:
        return {"error": str(e)}


@router.post("/register_ai_service")
async def register_ai_service(
    service_name: str = "langchain",
    endpoint: str = "https://jsonplaceholder.typicode.com/todos/1",
    option: str = "",
):
    try:
        return ai_service.create_service(service_name, endpoint, option)
    except Exception as e:
        return {"error": str(e)}
