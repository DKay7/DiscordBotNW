from config.economy.money_symbol import DEFAULT_MONEY_SYMBOL
from config.mod.mod_config import COGS_DIR
from config.bot.bot_config import PREFIX, TOKEN, OWNER_IDS, GUILD_ID, WARS_CHANNEL_ID, COMMON_RATING_CHANNEL_ID
from discord.ext.commands import Context, CommandNotFound, CommandOnCooldown, MissingPermissions, BadArgument
from discord.ext.commands import MissingRequiredArgument, PrivateMessageOnly, NoPrivateMessage
from config.bot.bot_config import COMMON_TEXT_CHANNEL_ID
from discord.ext.commands import Bot as BaseBot
from os.path import splitext, basename
from datetime import timedelta
from discord import Intents
from glob import glob

from utils.db.economy import get_money_symbol, add_money_symbol


class Bot(BaseBot):
    def __init__(self):
        self.PREFIX = PREFIX
        self.TOKEN = TOKEN
        self.OWNER_IDS = OWNER_IDS
        self.guild = None
        self.wars_channel = None
        self.common_rating_channel = None
        self.common_text_channel = None
        self.ready = False
        self.money_symbol = DEFAULT_MONEY_SYMBOL
        intents = Intents().all()
        super(Bot, self).__init__(command_prefix=self.PREFIX, owner_ids=self.OWNER_IDS, intents=intents)

    async def on_ready(self):
        if not self.ready:
            # for channel in self.guild.text_channels:
            #     await channel.send("I'm online now!")

            print(f'Logged in as {self.user}')
            self.ready = True
            self.guild = self.get_guild(GUILD_ID)
            self.wars_channel = self.guild.get_channel(WARS_CHANNEL_ID)
            self.common_rating_channel = self.guild.get_channel(COMMON_RATING_CHANNEL_ID)
            self.common_text_channel = self.guild.get_channel(COMMON_TEXT_CHANNEL_ID)

            self.money_symbol = get_money_symbol(self.guild.id)

            if not self.money_symbol:
                add_money_symbol(self.guild.id, DEFAULT_MONEY_SYMBOL)
                self.money_symbol = DEFAULT_MONEY_SYMBOL

        else:
            print(f'RE-Logged in as {self.user}')

    async def on_error(self, err, *args, **kwargs):
        if args and hasattr(args[0], "send"):
            await args[0].send("Возникла ошибка")
        raise

    async def on_command_error(self, ctx: Context, exc):
        if hasattr(exc, "original"):
            exc = exc.original

        if isinstance(exc, CommandNotFound):
            pass

        elif isinstance(exc, PrivateMessageOnly):
            await ctx.send(f'Команда может быть использована только в личных сообщениях с ботом')

        elif isinstance(exc, NoPrivateMessage):
            await ctx.send(f'Команда может быть использована только на сервере с ботом')

        elif isinstance(exc, CommandOnCooldown):
            delta_time = timedelta(seconds=exc.retry_after)
            delta_time_str = str(delta_time).split(".")[0]
            await ctx.send(f'Команда на колдауне. Попробуйте снова через {delta_time_str}')

        elif isinstance(exc, MissingPermissions):
            await ctx.send(f'У вас нет необходимых разрешений для запуска этой команды')

        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send(f"Не найден обязательный аргумент команды {exc.param.name}")

        elif isinstance(exc, BadArgument):
            await ctx.send("Некорректный аргумент команды")

        else:
            raise exc

    async def on_message(self, message):
        if not message.author == self.user and self.ready:
            await self.process_commands(message)

    def _setup(self):
        cogs = [splitext(basename(path))[0] for path in glob(COGS_DIR)]

        for cog in cogs:
            self.load_extension(f"bot.cogs.{cog}")

    def run(self, *args, **kwargs):
        self._setup()
        super().run(self.TOKEN, reconnect=True)

    @staticmethod
    async def on_connect():
        print("Bot connected")

    @staticmethod
    async def on_disconnect():
        print("Bot disconnected")
