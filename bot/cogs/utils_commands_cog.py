from discord import Member, Embed
from discord.ext.commands import Cog, command, Greedy
from typing import Optional
from config.utilities_commands.commands_data import ACTIONS
from utils.utilities_commands.embeds import get_avatar_embeds


class UtilsCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="get_avatar")
    async def get_avatar(self, ctx, user: Optional[Member]):
        user = user or ctx.author
        avatar_embed = get_avatar_embeds(user)
        await ctx.send(embed=avatar_embed)

    @command(name="utilities", aliases=list(ACTIONS.keys()))
    async def utilities(self, ctx, users: Greedy[Member]):
        pass


def setup(bot):
    bot.add_cog(UtilsCog(bot))
