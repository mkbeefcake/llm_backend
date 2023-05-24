
from core.firebase import db   
from db.schemas.service import ServiceSchema

def create_service(service: ServiceSchema):
    _old = get_service(service=service.service)
    if _old:
        return {"message": "Service registered successfully"}    

    service_doc_ref = db.collection("services").document(service.service)
    service_doc_ref.set({
        "service" : service.service,
        "endpoint" : service.endpoint,
        "option" : service.option
    })
    return {"message": "Service registered successfully"}

def get_service(service: str):
    service_doc_ref = db.collection("services").document(service)
    service_doc = service_doc_ref.get()
    if service_doc.exists:
        service_data = service_doc.to_dict()
        return service_data
    else:
        return None
    
def get_all_services():
    service_doc_ref = db.collection("services")
    collections = [doc.to_dict() for doc in service_doc_ref.stream()]
    if len(collections) > 0:
        return collections
    else:
        return None