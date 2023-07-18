import json

from core.task.task import TaskManager
from core.utils.log import BackLog
from db.cruds.chathistory import update_chat_histories
from providers.bridge import bridge


class ChatHistoryPipeline(TaskManager):
    def __init__(self):
        self.history_task_list = {}
        pass

    def stop_history_task(self, uid: any, provider_name: str, identifier_name: str):
        if (
            self.status_of_history_task(
                uid=uid, provider_name=provider_name, identifier_name=identifier_name
            )
            == True
        ):
            self.stop_task(self.history_task_list[uid][provider_name][identifier_name])
            result = bridge.disconnect(
                provider_name=provider_name, identifier_name=identifier_name
            )

        pass

    def status_of_history_task(
        self, uid: any, provider_name: str, identifier_name: str
    ):
        if (
            uid not in self.history_task_list
            or not provider_name in self.history_task_list[uid]
            or not identifier_name in self.history_task_list[uid][provider_name]
        ):
            return False
        else:
            if (
                self.history_task_list[uid][provider_name][identifier_name].done()
                == True
            ):
                return False

            return True

    def fetch_history_for_one(self, user_id, provider_name, identifier_name, user_data):
        print(f"****** Fetch History for one account *******")
        print(
            f"user: {user_id}, provider: {provider_name}, identifer: {identifier_name}"
        )

        try:
            if (
                self.status_of_history_task(
                    uid=user_id,
                    provider_name=provider_name,
                    identifier_name=identifier_name,
                )
                == True
            ):
                print(f"Get history is already launched")
                return

            if not user_id in self.history_task_list:
                self.history_task_list[user_id] = {}

            if not provider_name in self.history_task_list[user_id]:
                self.history_task_list[user_id][provider_name] = {}

            self.history_task_list[user_id][provider_name][
                identifier_name
            ] = self.create_onetime_task(
                ChatHistoryPipeline._fetch_history_func,
                user_id=user_id,
                provider_name=provider_name,
                identifier_name=identifier_name,
                user_data=json.dumps(user_data),
            )

        except Exception as e:
            BackLog.exception(instance=self, message=f"Exception occurred {str(e)}")
            pass

    async def _fetch_history_func(
        user_id: str, provider_name: str, identifier_name: str, user_data: str
    ):
        try:
            user_content = json.loads(user_data)
            await bridge.scrapy_all_chats(
                user_id=user_id,
                provider_name=provider_name,
                identifier_name=identifier_name,
                user_data=user_content,
                steper=ChatHistoryPipeline.update_history_on_db,
                option=None,
            )

            print(f"Get chat history: Done {user_id} - {identifier_name}")

        except Exception as e:
            BackLog.exception(
                instance=None,
                message=f"Exception occurred... {user_id} - {identifier_name}",
            )

        pass

    def update_history_on_db(
        user_id: str, provider_name: str, identifier_name: str, chat_histories: any
    ):
        BackLog.info(
            instance=None,
            message=f"{identifier_name}: Saving {len(chat_histories)} user's history on db....",
        )

        try:
            update_chat_histories(
                user_id=user_id,
                provider_name=provider_name,
                key=identifier_name,
                new_content=chat_histories,
            )

        except Exception as e:
            BackLog.exception(instance=None, message=f"Exception occurred to DB...")
            pass


chathistory_pipeline = ChatHistoryPipeline()
