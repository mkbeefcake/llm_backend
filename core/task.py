import asyncio
from core.bot.autobot import autobot
from core.timestamp import get_current_timestamp

class TaskManager:

    def __init__(self):
        self.task_list = {}
        pass

    async def task_func(user: any, interval: int):
        if interval < 0:
            return

        try:
            while True:
                start_timestamp = get_current_timestamp()
                print(f"Running Task...{start_timestamp}")
                await autobot.start(user)
                end_timestamp = get_current_timestamp()

                new_interval = interval + start_timestamp - end_timestamp
                if new_interval > 0:
                    await asyncio.sleep(new_interval)

        except asyncio.CancelledError:
            print(f'task_func: Received a request to cancel')

        pass

    def start_auto_bot(self, user: any, interval: int):
        if self.status_auto_bot(user) == False:
            self.task_list[user['uid']] = asyncio.create_task(TaskManager.task_func(user, interval))

        pass

    def stop_auto_bot(self, user: any):
        if user is not None and user['uid'] in self.task_list:           
            was_cancelled = self.task_list[user['uid']].cancel()
            print(f'stop_auto_bot: {was_cancelled}')
        pass
    
    # issue happens
    def status_auto_bot(self, user: any):
        if user is None or not user['uid'] in self.task_list:
            return False
        else:
            if self.task_list[user['uid']].done() == True:
                return False
            
            return True

task_manager = TaskManager()