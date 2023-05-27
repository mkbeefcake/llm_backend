import requests
from typing import Union
from fastapi import APIRouter, Depends
from db.cruds.service import create_service, get_all_services, get_service
from db.schemas.service import ServiceSchema
from .users import get_current_user, User

router = APIRouter()

@router.post("/get_ai_response")
async def get_ai_response(service_name: Union[str, None] = None, 
                          message: str = "Hi there", 
                          option: str = "",
                          curr_user: User = Depends(get_current_user)):  
    try:    
        if service_name:
            first_service = get_service(service=service_name)
        else:
            services = get_all_services()
            if not services:
                return {"message": "Error: There is no any AI s"}
        
            first_service = services[0]

        if not first_service["endpoint"]:
            return {"message": "Error: There is no endpoint for AI service"}
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(first_service["endpoint"], headers=headers, json={
            "message": message,
            "option": option
        })
        
        if response.status_code == 200:
            return {"message": response.json().message}
        else:
            return {"message": "Failed to get response"}
        
    except Exception as e:
        return {"error": str(e)}

@router.post("/register_ai_service")
async def register_ai_service(service: str = "langchain", endpoint: str = "https://jsonplaceholder.typicode.com/todos/1", option: str = ""):  
    try:
        return create_service(service=ServiceSchema(service, endpoint, option))
    except Exception as e:
        return {"error": str(e)}