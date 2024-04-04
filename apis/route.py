import os

from fastapi import APIRouter

from . import bots, messages, pipeline, providers, services, users, webhook

api_router = APIRouter()

BACKEND_TYPE = os.getenv("BACKEND_TYPE")

if BACKEND_TYPE == "MAIN":
    api_router.include_router(users.router, prefix="/users", tags=["users"])
    api_router.include_router(providers.router, prefix="/providers", tags=["providers"])
    api_router.include_router(bots.router, prefix="/bots", tags=["bots"])
    api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
    api_router.include_router(webhook.router, prefix="", tags=["webhook"])
elif (
    BACKEND_TYPE == "PRODUCT"
    or BACKEND_TYPE == "PURCHASED"
    or BACKEND_TYPE == "CHATHISTORY"
):
    api_router.include_router(pipeline.router, prefix="/pipeline", tags=["pipeline"])
else:
    api_router.include_router(users.router, prefix="/users", tags=["users"])
    api_router.include_router(providers.router, prefix="/providers", tags=["providers"])
    api_router.include_router(bots.router, prefix="/bots", tags=["bots"])
    api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
    api_router.include_router(pipeline.router, prefix="/pipeline", tags=["pipeline"])
    api_router.include_router(webhook.router, prefix="", tags=["webhook"])
