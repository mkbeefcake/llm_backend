from fastapi import APIRouter

from . import bots, messages, pipeline, providers, services, users

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(providers.router, prefix="/providers", tags=["providers"])
api_router.include_router(bots.router, prefix="/bots", tags=["bots"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(pipeline.router, prefix="/pipeline", tags=["pipeline"])
