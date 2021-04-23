from discord.ext.commands import Cog, Context, command, bot_has_permissions, has_permissions, Greedy
from discord.ext.commands.errors import MemberNotFound
from bot.embeds.mod_embeds import get_temp_ban_embed
from discord import Member, Embed
from asyncio import sleep
from typing import Optional


class Mod(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="temp_ban")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def temp_ban(self, ctx: Context, target: Member, duration: int, *,
                       reason: Optional[str] = "No reason provided"):

        link = await ctx.channel.create_invite(max_uses=1, unique=True)
        invite_embed = get_temp_ban_embed(duration, link)
        await target.send("Ждем вас!", embed=invite_embed)
        await target.ban(reason=reason)

        # TODO remove next line
        await ctx.send(f"Banned {target.mention}")
        await sleep(duration)

        await target.unban(reason="Temp. ban ended")
        # TODO remove next line
        await ctx.send(f"Unbanned {target.mention}")

    @command(name="ban")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def temp_ban(self, ctx: Context, targets: Greedy[Member], *,  reason: Optional[str] = "No reason provided"):

        for target in targets:
            await target.ban(reason=reason)
            # TODO remove next line
            await ctx.send(f"Banned {target.mention}")

    @command(name="echo")
    async def echo(self, ctx: Context, *, phrase: str):
        await ctx.message.delete()
        await ctx.send(phrase)


def setup(bot):
    bot.add_cog(Mod(bot))
