from glob import glob
from os.path import splitext, basename
from discord.ext.commands import Bot as BaseBot
from discord.ext.commands import MissingRequiredArgument
from config.config import TOKEN, PREFIX, OWNER_IDS, COGS_DIR
from discord.ext.commands import Context, CommandNotFound, CommandOnCooldown, MissingPermissions, BadArgument


class Bot(BaseBot):
    def __init__(self):
        self.PREFIX = PREFIX
        self.TOKEN = TOKEN
        self.OWNER_IDS = OWNER_IDS
        self.ready = False

        super(Bot, self).__init__(command_prefix=self.PREFIX, owner_ids=self.OWNER_IDS)

    async def on_ready(self):
        if not self.ready:
            for guild in self.guilds:
                for channel in guild.text_channels:
                    await channel.send("I'm online now!")

            print(f'Logged in as {self.user}')
            self.ready = True

        else:
            print(f'RE-Logged in as {self.user}')

    async def on_error(self, err, *args, **kwargs):
        await args[0].send("An error occurred")
        raise

    async def on_command_error(self, ctx: Context, exc):
        if isinstance(exc, CommandNotFound):
            pass

        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(f'This command is on cooldown. Try again in {exc.retry_after:,.2f} secs.')

        elif isinstance(exc, MissingPermissions):
            await ctx.send(f'You haven\'t permission to run this command')

        elif isinstance(exc, MissingRequiredArgument) or isinstance(exc, BadArgument):
            await ctx.send("One or more requirement arguments are missing")

        elif hasattr(exc, "original"):
            raise exc.original
        else:
            raise exc

    async def on_message(self, message):
        if not message.author == self.user:
            await self.process_commands(message)

    def setup(self):
        cogs = [splitext(basename(path))[0] for path in glob(COGS_DIR)]

        for cog in cogs:
            self.load_extension(f"bot.cogs.{cog}")

    def run(self, *args, **kwargs):
        self.setup()
        super().run(self.TOKEN, reconnect=True)

    @staticmethod
    async def on_connect():
        print("Bot connected")

    @staticmethod
    async def on_disconnect():
        print("Bot disconnected")
