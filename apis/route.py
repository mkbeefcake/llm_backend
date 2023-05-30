from fastapi import APIRouter

from . import providers, services, users

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(providers.router, prefix="/providers", tags=["providers"])
