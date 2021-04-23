from typing import Optional
from discord.utils import get
from discord import Embed
from discord.ext.commands import Cog, command, Context
from discord.ext.commands.core import Command


def syntax(command: Command):
    params = []
    for key, value in command.params.items():
        if key not in ("self", "ctx"):
            params.append(f"[{key}]" if "NoneType" in str(value) else f"<{key}>")

    params = " ".join(params)

    return f"""{command} {'|'.join(*command.aliases) if command.aliases else ''} {params if params else ''}"""


class Help(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    async def cmd_help(self, ctx: Context, command: Command):
        print(syntax(command))
        help_embed = Embed(title=f"Help with `{command}`",
                           description=syntax(command),
                           colour=ctx.author.colour)

        help_embed.add_field(name="Command description", value=command.help)

        await ctx.send(embed=help_embed)

    @command(name="help")
    async def show_help(self, ctx: Context, command: Optional[str]):
        """This command shows help message"""
        if command is None:
            pass
        else:
            if cmd := get(self.bot.commands, name=command):
                await self.cmd_help(ctx, cmd)
            else:
                await ctx.send("That command doesn't exist")


def setup(bot):
    bot.add_cog(Help(bot))