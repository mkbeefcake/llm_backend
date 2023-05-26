import requests
from fastapi import APIRouter
from db.cruds.service import create_service, get_all_services
from db.schemas.service import ServiceSchema

router = APIRouter()

@router.post("/test_ai_endpoint")
async def test_ai_endpoint(message: str, option: str):
    print(message, option)
    return {"message":"Success to checking"}

# @router.post("/get_response")
# async def get_response(proxy_name: str = "google", email: str = "test@gmail.com", message: str = "Hi there", option: str = ""):  
#     proxy = get_proxy(proxy=proxy_name)
#     if not proxy:
#         return {"message": "Error: this bot is not registered"}
    
#     services = get_all_services()
#     if not services:
#         return {"message": "Error: There is no any AI s"}
    
#     first_service = services[0]
#     if not first_service["endpoint"]:
#         return {"message": "Error: There is no endpoint for AI service"}
    
#     headers = {"Content-Type": "application/json"}
#     try:
#         response = requests.post(first_service["endpoint"], headers=headers, json={
#             "message": message,
#             "option": option
#         })
        
#         if response.status_code == 200:
#             return {"message": response.json().message}
#         else:
#             return {"message": "Failed to get response"}
#     except:
#         return {"message": "Failed to get response"}

@router.post("/register_ai_service")
async def register_ai_service(service: str = "langchain", endpoint: str = "http://localhost:8000/services/test_ai_endpoint", option: str = ""):  
    return create_service(service=ServiceSchema(service, endpoint, option))