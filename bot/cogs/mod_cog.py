from discord.ext.commands import Cog, Context, command, bot_has_permissions, has_permissions, Greedy
from discord.ext.commands import Converter, BadArgument
from bot.embeds.mod_embeds import get_temp_ban_embed
from discord import Member, Object, NotFound
from discord.utils import find
from typing import Optional
from asyncio import sleep


class BannedUser(Converter):
    async def convert(self, ctx, arg):
        if ctx.guild.me.guild_permissions.ban_members:
            if arg.isdigit():
                try:
                    return (await ctx.guild.fetch_ban(Object(id=int(arg)))).user
                except NotFound:
                    raise BadArgument

            banned_users = [e.user for e in await ctx.guild.bans()]
            if banned_users:
                if (user := find(lambda u: str(u) == arg, banned_users)) is not None:
                    return user
                else:
                    raise BadArgument


class Mod(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="temp_ban")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def temp_ban_user(self, ctx: Context, targets: Greedy[Member], duration: int,  *,
                            reason: Optional[str] = "No reason provided"):

        if not targets or not duration:
            raise BadArgument

        for target in targets:
            link = await ctx.channel.create_invite(max_uses=1, unique=True)
            invite_embed = get_temp_ban_embed(duration, link)
            await target.send("Ждем вас!", embed=invite_embed)
            await target.ban(reason=reason)

            # TODO remove next line
            await ctx.send(f"Banned {target.mention}")

        await sleep(duration)

        for target in targets:
            try:
                await target.unban(reason="Temp. ban ended")
                # TODO remove next line
                await ctx.send(f"Unbanned {target.mention}")
            except NotFound:
                pass

    @command(name="ban")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def ban_user(self, ctx: Context, targets: Greedy[Member], *,  reason: Optional[str] = "No reason provided"):

        if not targets:
            raise BadArgument

        for target in targets:
            if ctx.guild.me.top_role.position > target.top_role.position \
                    and not target.guild_permissions.administrator:
                await target.ban(reason=reason)
                # TODO remove next line
                await ctx.send(f"Banned {target.mention}")
            else:
                await ctx.send(f"{target.mention} could not be banned")

    @command(name="unban")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def unban_user(self, ctx: Context, targets: Greedy[BannedUser], *,
                         reason: Optional[str] = "No reason provided"):
        if not targets:
            raise BadArgument

        for target in targets:
            await ctx.guild.unban(target, reason=reason)
            # TODO remove next line
            await ctx.send(f"Unbanned {target.mention}")

    @command(name="kick")
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick_user(self, ctx: Context, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided"):

        if not targets:
            raise BadArgument

        for target in targets:
            if ctx.guild.me.top_role.position > target.top_role.position \
                    and not target.guild_permissions.administrator:
                await target.kick(reason=reason)
                # TODO remove next line
                await ctx.send(f"Kicked {target.mention}")
            else:
                await ctx.send(f"{target.mention} could not be Kicked")

    @command(name="clear", aliases=['cls'])
    @has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):

        if not amount:
            raise BadArgument

        await ctx.channel.purge(limit=(amount + 1))

    @command(name="echo")
    async def echo(self, ctx: Context, *, phrase: str):
        if not phrase:
            raise BadArgument

        await ctx.message.delete()
        await ctx.send(phrase)


def setup(bot):
    bot.add_cog(Mod(bot))
