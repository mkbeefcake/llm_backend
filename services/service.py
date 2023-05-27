import requests
from db.cruds.service import create_service, get_all_services, get_service
from db.schemas.service import ServiceSchema

class Service:

    def __init__(self):
        pass

    def create_service(self, service_name: str, endpoint: str, option):
        return create_service(service=ServiceSchema(service=service_name, 
                                                    endpoint=endpoint, 
                                                    option=option))
    

    def get_response(self, service_name: str, message: str, option):
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

        # Original code
        # response = requests.post(first_service["endpoint"], headers=headers, json={
        #     "message": message,
        #     "option": option
        # })

        # if response.status_code == 200:
        #     return {"message": response.json().message}
        # else:
        #     return {"message": "Failed to get response"}

        # Mockup code
        return {"message": "Mockup response from Mockup AI service"}


ai_service = Service()