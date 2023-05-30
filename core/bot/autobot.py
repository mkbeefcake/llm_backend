import os

from core.bot.base import BaseProviderBot
from core.loader.loader import Loader
from db.cruds.users import get_user_data

BOTS_PATH = os.path.join(os.path.dirname(__file__), "plugins")


class AutoBot:
    def __init__(self):
        self.loader = Loader()
        self.bots = self.loader.load_plugins(BOTS_PATH, BaseProviderBot, recursive=True)
        self.bot_list = {}

        # load bot instances
        for key in self.bots:
            Bot = self.bots[key]
            self.bot_list[key] = Bot()

    async def start(self, user: any):
        user_id = user["uid"]
        user_data = get_user_data(user_id)

        for key in user_data:
            bot_name = key + "bot"
            bot = self.bot_list[bot_name.lower()]
            if bot:
                await bot.start(user_data[key])

        pass


autobot = AutoBot()
