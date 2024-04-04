import requests
from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from providers.nango import NangoEventData

router = APIRouter()

@router.post(
    "/nango_sync_webhook",
    summary="Nango Sync event webhook",
    description="This endpoint is called from Nango Provider which indicates the new synchronized data is available",
    response_model=None
)
async def nango_sync_webhook(event_data: NangoEventData):
    print(f"{event_data}")
    pass