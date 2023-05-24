
from core.firebase import db   
from db.schemas.proxy import ProxySchema

def create_proxy(proxy: ProxySchema):
    _old = get_proxy(proxy=proxy.proxy)
    if _old:
        return {"message": "proxy registered successfully"}    

    proxy_doc_ref = db.collection("proxies").document(proxy.proxy)
    proxy_doc_ref.set({
        "proxy" : proxy.proxy,
        "option" : proxy.option
    })
    return {"message": "proxy registered successfully"}

def get_proxy(proxy: str):
    proxy_doc_ref = db.collection("proxies").document(proxy)
    proxy_doc = proxy_doc_ref.get()
    if proxy_doc.exists:
        proxy_data = proxy_doc.to_dict()
        return proxy_data
    else:
        return None
    
def get_all_proxies():
    proxy_doc_ref = db.collection("proxies")
    collections = [doc.to_dict() for doc in proxy_doc_ref.stream()]
    if len(collections) > 0:
        return collections
    else:
        return None