from fastapi import APIRouter

from core.pipeline.products import products_pipeline
from core.utils.message import MessageErr, MessageOK

router = APIRouter()


@router.post("/fetch_purchased_products")
async def fetch_purchased_products():
    try:
        products_pipeline.fetch_purchased_products()
        return MessageOK(
            data={"message": "User started import_purchased_products successfully"}
        )
    except Exception as e:
        return MessageErr(reason=str(e))


@router.post("/fetch_all_products")
async def fetch_all_products():
    try:
        products_pipeline.fetch_all_products()
        return MessageOK(
            data={"message": "User started import_all_products successfully"}
        )
    except Exception as e:
        return MessageErr(reason=str(e))
