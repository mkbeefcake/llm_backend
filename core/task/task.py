import asyncio

from core.utils.log import BackLog
from core.utils.timestamp import get_current_timestamp


class TaskManager:
    def __init__(self):
        pass

    async def internal_func(self, task_func: any, interval: int, **kwargs):
        if interval < 0:
            return

        try:
            while True:
                BackLog.info(instance=self, message=f"Running Task...")

                start_timestamp = get_current_timestamp()
                await task_func(**kwargs)
                end_timestamp = get_current_timestamp()

                new_interval = interval + start_timestamp - end_timestamp
                if new_interval > 0:
                    await asyncio.sleep(new_interval)

        except asyncio.CancelledError:
            BackLog.info(
                instance=self,
                message=f"task_func: Received a request to cancel",
            )

        except Exception as e:
            BackLog.exception(instance=self, message=f"Exception occurred")

        pass

    def create_task(self, task_func: any, interval: int, **kwargs):
        return asyncio.create_task(self.internal_func(task_func, interval, **kwargs))

    def stop_task(self, task: any):
        task.cancel()
