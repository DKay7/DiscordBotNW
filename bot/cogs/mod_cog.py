from discord.ext.commands import Cog, Context, command, bot_has_permissions, has_permissions, Greedy
from discord.ext.commands import Converter, BadArgument, MissingPermissions
from bot.embeds.mod_embeds import send_temp_ban_embeds, send_ban_embeds,  send_kick_embeds
from bot.embeds.mod_embeds import send_mute_embeds, send_unmute_embeds
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


class ToSeconds(Converter):
    def __init__(self):
        self.minutes = 0
        self.hours = 0

    async def convert(self, ctx, arg):
        time_type = arg[-1]

        if time_type not in ['h', 'm'] or not (arg := arg[:-1]).isdigit():
            raise BadArgument

        if time_type == 'h':
            self.hours = int(arg)
        elif time_type == 'm':
            self.minutes = int(arg)

        return self

    def __str__(self):
        return f"{self.hours} часов, {self.minutes} минут"

    def get_hours(self) -> int:
        return self.hours

    def get_minutes(self) -> int:
        return self.minutes

    def get_seconds(self) -> int:
        return self.minutes * 60 + self.hours * 3600


class Mod(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.text_mute_role = None
        self.voice_mute_role = None

    @command(name="temp_ban")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def temp_ban_user(self, ctx: Context, targets: Greedy[Member], time: ToSeconds(), *,
                            reason: Optional[str] = "No reason provided"):

        if not targets or not time:
            raise BadArgument

        for target in targets:
            if ctx.guild.me.top_role.position > target.top_role.position \
                    and not target.guild_permissions.administrator:
                link = await ctx.channel.create_invite(max_uses=1, unique=True)

                await send_temp_ban_embeds(target, time.__str__(), link, reason)
                await target.ban(reason=reason)

                # TODO remove next line
                await ctx.send(f"Banned {target.mention}", delete_after=10)

            else:
                raise MissingPermissions

        await sleep(time.get_seconds())

        for target in targets:
            try:
                await target.unban(reason="Temp. ban ended")
                # TODO remove next line
                await ctx.send(f"Unbanned {target.mention}", delete_after=10)
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

                await send_ban_embeds(target, reason)
                await target.ban(reason=reason)

                # TODO remove next line
                await ctx.send(f"Banned {target.mention}", delete_after=10)
            else:
                raise MissingPermissions

    @command(name="unban")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def unban_user(self, ctx: Context, targets: Greedy[BannedUser], *,
                         reason: Optional[str] = "No reason provided"):
        if not targets:
            raise BadArgument

        for target in targets:
            try:
                await ctx.guild.unban(target, reason=reason)
                # TODO remove next line
                await ctx.send(f"Unbanned {target.mention}", delete_after=10)
            except NotFound:
                await ctx.send(f"Пользователь {target.mention} не найден среди забаненных")

    @command(name="kick")
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick_user(self, ctx: Context, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided"):

        if not targets:
            raise BadArgument

        for target in targets:
            if ctx.guild.me.top_role.position > target.top_role.position \
                    and not target.guild_permissions.administrator:

                link = await ctx.channel.create_invite(max_uses=1, unique=True)

                await send_kick_embeds(target, link, reason)
                await target.kick(reason=reason)

                # TODO remove next line
                await ctx.send(f"Kicked {target.mention}", delete_after=10)
            else:
                raise MissingPermissions

    @command(name="clear", aliases=['cls'])
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):

        if not amount:
            raise BadArgument

        with ctx.channel.typing():
            await ctx.message.delete()
            await ctx.channel.purge(limit=amount)

    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    @command(name="mute")
    async def mute_user(self, ctx: Context, targets: Greedy[Member], time: ToSeconds(), mute_type: str = "all", *,
                        reason: Optional[str] = "No reason provided"):

        if not targets or mute_type not in ["all", "text", "voice"]:
            raise BadArgument

        for target in targets:
            if ctx.guild.me.top_role.position > target.top_role.position \
                    and not target.guild_permissions.administrator:

                for channel in ctx.guild.channels:
                    perms = channel.overwrites_for(target)

                    if mute_type == "text":
                        perms.send_messages = False
                    elif mute_type == "voice":
                        perms.speak = False
                    elif mute_type == "all":
                        perms.send_messages = False
                        perms.speak = False

                    await channel.set_permissions(target, overwrite=perms)

                # TODO remove next line
                await ctx.send(f"Muted {target.mention}", delete_after=10)

                await send_mute_embeds(target, time.__str__(), reason)

            else:
                raise MissingPermissions

        await sleep(time.get_seconds())
        await self.unmute_user(ctx, targets, unmute_type=mute_type)

    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    @command(name="unmute")
    async def unmute_user(self, ctx: Context, targets: Greedy[Member], unmute_type: str = "all"):

        if not targets or unmute_type not in ["all", "text", "voice"]:
            raise BadArgument

        for target in targets:
            if ctx.guild.me.top_role.position > target.top_role.position \
                    and not target.guild_permissions.administrator:

                for channel in ctx.guild.channels:
                    perms = ctx.channel.overwrites_for(target)

                    if unmute_type == "text":
                        perms.send_messages = True
                    elif unmute_type == "voice":
                        perms.speak = True
                    elif unmute_type == "all":
                        perms.send_messages = True
                        perms.speak = True

                    await channel.set_permissions(target, overwrite=perms)

                await send_unmute_embeds(target)

                # TODO remove next line
                await ctx.send(f"Unmuted {target.mention}", delete_after=10)
            else:
                raise MissingPermissions

    @command(name="echo")
    async def echo(self, ctx: Context, *, phrase: str):
        if not phrase:
            raise BadArgument

        await ctx.message.delete()
        await ctx.send(phrase)


def setup(bot):
    bot.add_cog(Mod(bot))
