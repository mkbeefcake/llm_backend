import asyncio

from core.bot.autobot import autobot
from core.log import BackLog
from core.timestamp import get_current_timestamp


class TaskManager:
    def __init__(self):
        self.task_list = {}
        self.task_status_list = {}
        pass

    async def task_func(
        user: any, provider_name: str, identifier_name: str, interval: int
    ):
        if interval < 0:
            return

        try:
            while True:
                BackLog.info(instance=task_manager, message=f"Running Task...")

                start_timestamp = get_current_timestamp()
                await autobot.start(user, provider_name, identifier_name)
                end_timestamp = get_current_timestamp()

                new_interval = interval + start_timestamp - end_timestamp
                if new_interval > 0:
                    await asyncio.sleep(new_interval)

        except asyncio.CancelledError:
            BackLog.info(
                instance=task_manager,
                message=f"task_func: Received a request to cancel",
            )

        except Exception as e:
            BackLog.exception(instance=task_manager, message=f"Exception occurred")

        pass

    def start_auto_bot(
        self, user: any, provider_name: str, identifier_name: str, interval: int
    ):
        if user is None:
            return

        uid = user["uid"]

        if self.status_auto_bot(user, provider_name, identifier_name) == False:
            if not uid in self.task_list:
                self.task_list[uid] = {}

            if not uid in self.task_status_list:
                self.task_status_list[uid] = {}

            if not provider_name in self.task_list[uid]:
                self.task_list[uid][provider_name] = {}

            if not provider_name in self.task_status_list[uid]:
                self.task_status_list[uid][provider_name] = {}

            self.task_list[uid][provider_name][identifier_name] = asyncio.create_task(
                TaskManager.task_func(user, provider_name, identifier_name, interval)
            )
            self.task_status_list[uid][provider_name][identifier_name] = True

        pass

    def stop_auto_bot(self, user: any, provider_name: str, identifier_name: str):
        uid = user["uid"]

        if (
            user is not None
            and uid in self.task_list
            and provider_name in self.task_list[uid]
            and identifier_name in self.task_list[uid][provider_name]
        ):
            was_cancelled = self.task_list[uid][provider_name][identifier_name].cancel()
            self.task_status_list[uid][provider_name][identifier_name] = False
            BackLog.info(
                instance=task_manager, message=f"stop_auto_bot: {was_cancelled}"
            )
        pass

    # issue happens
    def status_auto_bot(self, user: any, provider_name: str, identifier_name: str):
        if (
            user is None
            or not user["uid"] in self.task_list
            or not provider_name in self.task_list[user["uid"]]
            or not identifier_name in self.task_list[user["uid"]][provider_name]
        ):
            return False
        else:
            uid = user["uid"]
            if self.task_list[uid][provider_name][identifier_name].done() == True:
                return False

            return True

    def status_my_auto_bot(self, user: any):
        if user is None or not user["uid"] in self.task_status_list:
            return {}
        else:
            return self.task_status_list[user["uid"]]


task_manager = TaskManager()
