from fastapi import APIRouter, Depends

from core.message import MessageErr, MessageOK
from providers.bridge import bridge

from .users import User, get_current_user

router = APIRouter()


@router.get("/get_product_list")
async def get_product_list(
    provider_name: str = "replicateprovider",
    curr_user: User = Depends(get_current_user),
):
    try:
        return MessageOK(data=await bridge.get_product_list(provider_name))
    except Exception as e:
        return MessageErr(reason=str(e))


@router.get("/get_bestseller_products")
async def get_bestseller_products(
    provider_name: str = "replicateprovider",
    curr_user: User = Depends(get_current_user),
):
    try:
        return MessageOK(data=await bridge.get_bestseller_products(provider_name))
    except Exception as e:
        return MessageErr(reason=str(e))
