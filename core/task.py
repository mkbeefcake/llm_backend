import asyncio

from core.bot.autobot import autobot
from core.timestamp import get_current_timestamp


class TaskManager:
    def __init__(self):
        self.task_list = {}
        self.task_status_list = {}
        pass

    async def task_func(user: any, provider_name: str, interval: int):
        if interval < 0:
            return

        try:
            while True:
                start_timestamp = get_current_timestamp()
                print(f"Running Task...{start_timestamp}")
                await autobot.start(user, provider_name)
                end_timestamp = get_current_timestamp()

                new_interval = interval + start_timestamp - end_timestamp
                if new_interval > 0:
                    await asyncio.sleep(new_interval)

        except asyncio.CancelledError:
            print(f"task_func: Received a request to cancel")

        pass

    def start_auto_bot(self, user: any, provider_name: str, interval: int):
        if self.status_auto_bot(user, provider_name) == False:
            if not user["uid"] in self.task_list:
                self.task_list[user["uid"]] = {}

            if not user["uid"] in self.task_status_list:
                self.task_status_list[user["uid"]] = {}

            self.task_list[user["uid"]][provider_name] = asyncio.create_task(
                TaskManager.task_func(user, provider_name, interval)
            )
            self.task_status_list[user["uid"]][provider_name] = True

        pass

    def stop_auto_bot(self, user: any, provider_name: str):
        if (
            user is not None
            and user["uid"] in self.task_list
            and provider_name in self.task_list[user["uid"]]
        ):
            was_cancelled = self.task_list[user["uid"]][provider_name].cancel()
            self.task_status_list[user["uid"]][provider_name] = False
            print(f"stop_auto_bot: {was_cancelled}")
        pass

    # issue happens
    def status_auto_bot(self, user: any, provider_name: str):
        if (
            user is None
            or not user["uid"] in self.task_list
            or not provider_name in self.task_list[user["uid"]]
        ):
            return False
        else:
            if self.task_list[user["uid"]][provider_name].done() == True:
                return False

            return True

    def status_my_auto_bot(self, user: any):
        if user is None or not user["uid"] in self.task_status_list:
            return {}
        else:
            return self.task_status_list[user["uid"]]


task_manager = TaskManager()
