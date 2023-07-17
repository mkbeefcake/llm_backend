from fastapi import APIRouter

from core.pipeline.products import products_pipeline
from core.pipeline.chathistories import chathistory_pipeline
from core.utils.message import MessageErr, MessageOK
from db.cruds.users import get_user_data

router = APIRouter()

@router.post("/get_chat_history_for_one")
async def get_chat_history_for_one(user_id, provider_name, identifier_name):
    try:
        user_data = get_user_data(user_id)
        await chathistory_pipeline.fetch_history_for_one(
            user_id,
            provider_name,
            identifier_name,
            user_data=user_data[provider_name][identifier_name],
        )

        return MessageOK(
            data={
                "message": "User started import_chat_history_for_one successfully"
            }
        )
    except Exception as e:
        return MessageErr(reason=str(e))

@router.post("/stop_chat_history_for_one")
async def stop_chat_history_for_one(user_id, provider_name, identifier_name):
    try:
        await chathistory_pipeline.stop_history_task(
            uid=user_id, provider_name=provider_name, identifier_name=identifier_name
        )
        return MessageOK(data={"message": "User stopped chat_history-bot successfully"})
    except Exception as e:
        return MessageErr(reason=str(e))

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


@router.post("/fetch_purchased_products_for_one")
async def fetch_purchased_products_for_one(user_id, provider_name, identifier_name):
    try:
        user_data = get_user_data(user_id)
        await products_pipeline.fetch_purchased_products_for_one(
            user_id,
            provider_name,
            identifier_name,
            user_data=user_data[provider_name][identifier_name],
        )

        return MessageOK(
            data={
                "message": "User started import_purchased_products_for_one successfully"
            }
        )
    except Exception as e:
        return MessageErr(reason=str(e))


@router.post("/fetch_all_products_for_one")
async def fetch_all_products_for_one(user_id, provider_name, identifier_name):
    try:
        user_data = get_user_data(user_id)
        await products_pipeline.fetch_all_products_for_one(
            user_id,
            provider_name,
            identifier_name,
            user_data=user_data[provider_name][identifier_name],
        )

        return MessageOK(
            data={"message": "User started import_all_products_for_one successfully"}
        )
    except Exception as e:
        return MessageErr(reason=str(e))


@router.post("/stop_purchased_products_for_one")
async def stop_purchased_products_for_one(user_id, provider_name, identifier_name):
    try:
        await products_pipeline.stop_purchased_products_task(
            uid=user_id, provider_name=provider_name, identifier_name=identifier_name
        )
        return MessageOK(data={"message": "User stopped purchased-bot successfully"})
    except Exception as e:
        return MessageErr(reason=str(e))


@router.post("/stop_all_products_for_one")
async def stop_all_products_for_one(user_id, provider_name, identifier_name):
    try:
        await products_pipeline.stop_all_products_task(
            uid=user_id, provider_name=provider_name, identifier_name=identifier_name
        )
        return MessageOK(data={"message": "User stopped all-product-bot successfully"})
    except Exception as e:
        return MessageErr(reason=str(e))
