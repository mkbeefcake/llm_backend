from core.firebase import db
from db.schemas.provider import ProviderSchema


def create_provider(provider: ProviderSchema):
    _old = get_provider(provider_name=provider.provider_name)
    if _old:
        return {"message": "Provider registered successfully"}

    provider_doc_ref = db.collection("providers").document(provider.provider_name)
    provider_doc_ref.set(
        {
            "provider": provider.provider_name,
            "provider_description": provider.provider_description,
            "provider_icon_url": provider.provider_icon_url,
        }
    )
    return {"message": "Provider registered successfully"}


def get_provider(provider_name: str):
    provider_doc_ref = db.collection("providers").document(provider_name)
    provider_doc = provider_doc_ref.get()
    if provider_doc.exists:
        provider_data = provider_doc.to_dict()
        return provider_data
    else:
        return None


def get_all_providers():
    provider_doc_ref = db.collection("providers")
    collections = [doc.to_dict() for doc in provider_doc_ref.stream()]
    if len(collections) > 0:
        return collections
    else:
        return None
