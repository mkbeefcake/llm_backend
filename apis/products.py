from fastapi import APIRouter

router = APIRouter()

@router.post("/fetch_purchased_products")
async def fetch_purchased_products(
):
    pass

@router.post("/fetch_all_products")
async def fetch_all_products(
):
    pass