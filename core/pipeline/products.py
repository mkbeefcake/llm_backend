import json

from core.task.task import TaskManager
from db.cruds.product import update_products
from db.cruds.purchased import get_last_message_ids, update_purchased
from db.cruds.users import get_all_users_data
from products.pinecone import pinecone_service
from providers.bridge import bridge


class ProductPipeline(TaskManager):
    def __init__(self) -> None:
        self.purchased_task_list = {}
        self.allproducts_task_list = {}
        pass

    """
    Purchased Product pipeline
    """

    async def _fetch_purchased_products_func(
        user_id: str, provider_name: str, identifier_name: str, user_data: str
    ):
        try:
            user_content = json.loads(user_data)
            last_message_ids = get_last_message_ids(
                user_id=user_id, provider_name=provider_name, key=identifier_name
            )
            purchased_info = await bridge.get_purchased_products(
                provider_name=provider_name,
                identifier_name=identifier_name,
                user_data=user_content,
                option={"last_message_ids": last_message_ids},
            )
            update_purchased(
                user_id=user_id,
                provider_name=provider_name,
                key=identifier_name,
                new_content=purchased_info,
            )

            print(f"Import purchases : Done, {user_id}")

        except Exception as e:
            print(f"Exception occurred : {str(e)}")
        pass

    def fetch_purchased_products(self):
        print(f"****** Fetch Purchased Products *******")
        all_user_info = get_all_users_data()
        for user_info in all_user_info:
            # get user id
            uid = list(user_info.keys())[0]
            content = user_info[uid]
            print(f"UID: {uid}")

            # iterate providers
            for provider_name in list(content.keys()):
                print(f"|-- Provider: {provider_name}")

                for identifier_name in list(content[provider_name].keys()):
                    print(f"|---- Identifier: {identifier_name}")

                    user_data = json.dumps(content[provider_name][identifier_name])
                    if (
                        self.status_of_purchased_products_task(
                            uid, provider_name, identifier_name
                        )
                        == False
                    ):
                        if not uid in self.purchased_task_list:
                            self.purchased_task_list[uid] = {}

                        if not provider_name in self.purchased_task_list[uid]:
                            self.purchased_task_list[uid][provider_name] = {}

                        self.purchased_task_list[uid][provider_name][
                            identifier_name
                        ] = self.create_onetime_task(
                            ProductPipeline._fetch_purchased_products_func,
                            user_id=uid,
                            provider_name=provider_name,
                            identifier_name=identifier_name,
                            user_data=user_data,
                        )

        pass

    def status_of_purchased_products_task(
        self, uid: any, provider_name: str, identifier_name: str
    ):
        if (
            uid not in self.purchased_task_list
            or not provider_name in self.purchased_task_list[uid]
            or not identifier_name in self.purchased_task_list[uid][provider_name]
        ):
            return False
        else:
            if (
                self.purchased_task_list[uid][provider_name][identifier_name].done()
                == True
            ):
                return False

            return True

    """
    All Products pipeline
    """

    async def _fetch_all_products_func(
        user_id: str, provider_name: str, identifier_name: str, user_data: str
    ):
        try:
            user_content = json.loads(user_data)
            products_info = await bridge.get_all_products(
                provider_name=provider_name,
                identifier_name=identifier_name,
                user_data=user_content,
            )

            # save these to DB
            update_products(
                user_id=user_id,
                provider_name=provider_name,
                key=identifier_name,
                new_content=products_info["products"],
            )

            # pass it to AI service : Pinecone service
            if provider_name == "replicateprovider":
                pinecone_service.update_products(
                    products_info=products_info,
                    option={
                        "namespace": f"{provider_name}_{user_id}_{identifier_name}"
                    },
                )
            elif provider_name == "gmailprovider":
                pass

            print(f"Import products : Done, {user_id}")
        except Exception as e:
            print(f"Exception occurred : {str(e)}")
        pass

    def fetch_all_products(self):
        print(f"****** Fetch All Products *******")
        all_user_info = get_all_users_data()
        for user_info in all_user_info:
            # get user id
            uid = list(user_info.keys())[0]
            content = user_info[uid]
            print(f"UID: {uid}")

            # iterate providers
            for provider_name in list(content.keys()):
                print(f"|-- Provider: {provider_name}")

                for identifier_name in list(content[provider_name].keys()):
                    print(f"|---- Identifier: {identifier_name}")

                    user_data = json.dumps(content[provider_name][identifier_name])
                    if (
                        self.status_of_all_products_task(
                            uid, provider_name, identifier_name
                        )
                        == False
                    ):
                        if not uid in self.allproducts_task_list:
                            self.allproducts_task_list[uid] = {}

                        if not provider_name in self.allproducts_task_list[uid]:
                            self.allproducts_task_list[uid][provider_name] = {}

                        self.allproducts_task_list[uid][provider_name][
                            identifier_name
                        ] = self.create_onetime_task(
                            ProductPipeline._fetch_all_products_func,
                            user_id=uid,
                            provider_name=provider_name,
                            identifier_name=identifier_name,
                            user_data=user_data,
                        )

        pass

    def status_of_all_products_task(
        self, uid: any, provider_name: str, identifier_name: str
    ):
        if (
            uid not in self.allproducts_task_list
            or not provider_name in self.allproducts_task_list[uid]
            or not identifier_name in self.allproducts_task_list[uid][provider_name]
        ):
            return False
        else:
            if (
                self.allproducts_task_list[uid][provider_name][identifier_name].done()
                == True
            ):
                return False

            return True


products_pipeline = ProductPipeline()
