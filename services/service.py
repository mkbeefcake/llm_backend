import requests

from core.config import settings
from core.utils.message import MessageErr, MessageOK
from db.cruds.service import create_service, get_all_services, get_service
from db.schemas.service import ServiceSchema
from services.llm.services import (  # huggingface_service,
    banana_service,
    http_service,
    openai_service,
    replica_service,
    textgen_service,
)

LLM_SERVICE_ENDPOINT = "http://195.60.167.43:10458/api/v1/predict"


class Service:
    def __init__(self):
        pass

    def create_service(self, service_name: str, endpoint: str, option):
        return create_service(
            service=ServiceSchema(
                service=service_name, endpoint=endpoint, option=option
            )
        )

    def get_response(self, service_name: str, message: str = None, option: any = None):
        if service_name == "openai_service":
            result = openai_service.get_response(message=message, option="")
        elif service_name == "banana_service":
            result = banana_service.get_response(message=message, option="")
        elif service_name == "replica_service":
            result = replica_service.get_response(message=message, option=option)
        elif service_name == "textgen_service":
            result = textgen_service.get_response(message=message, option=option)
        # elif service_name == "huggingface_service":
        #    result = huggingface_service.get_response(message=message, option=option)
        else:
            result = http_service.get_response(message=message, option="")

        return {"message": result}

        # headers = {"Content-Type": "application/json"}
        # response = requests.post(
        #     LLM_SERVICE_ENDPOINT, headers=headers, json={"input_text": message}
        # )
        # return {"message": response.json()["result"]}

        # # if service_name:
        # #     first_service = get_service(service=service_name)
        # # else:
        # #     services = get_all_services()
        # #     if not services:
        # #         return {"message": "Error: There is no any AI s"}

        # #     first_service = services[0]

        # # if not first_service["endpoint"]:
        # #     return {"message": "Error: There is no endpoint for AI service"}

        # # headers = {"Content-Type": "application/json"}

        # # # Original code
        # # # response = requests.post(first_service["endpoint"], headers=headers, json={
        # # #     "message": message,
        # # #     "option": option
        # # # })

        # # # if response.status_code == 200:
        # # #     return {"message": response.json().message}
        # # # else:
        # # #     return {"message": "Failed to get response"}

        # # # Mockup code
        # # return {"message": "Mockup response from Mockup AI service"}


ai_service = Service()
