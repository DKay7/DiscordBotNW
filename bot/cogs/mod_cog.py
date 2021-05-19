from utils.db.db_mod_utils import get_all_temp_role_entries, get_all_temp_ban_entries, get_all_temp_mute_entries
from utils.db.db_mod_utils import delete_temp_role_entry, delete_temp_ban_entry, delete_temp_mute_entry
from utils.db.db_mod_utils import add_temp_role_entry, add_temp_ban_entry, add_temp_mute_entry
from utils.db.db_mod_utils import get_temp_role_entry, get_temp_ban_entry, get_temp_mute_entry
from utils.db.db_mod_utils import update_warn_entry, get_warn_entry, unwarn_entry

from discord.ext.commands import Cog, Context, command, bot_has_permissions, has_permissions, MissingRequiredArgument
from bot.embeds.mod_embeds import send_temp_ban_embeds, send_ban_embeds,  send_kick_embeds
from bot.embeds.mod_embeds import send_mute_embeds, send_unmute_embeds, send_warn_embeds
from discord.ext.commands import BadArgument, MissingPermissions
from config.bot_config import NUM_WARNS_TO_TEMP_BAN, TIME_TO_TEMP_BAN
from discord import Member, Object, NotFound, User, Role
from datetime import datetime, timedelta
from typing import Optional
from asyncio import sleep

from utils.mod_utils.data_converters import BannedUser, TimeConverter


class Mod(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.text_mute_role = None
        self.voice_mute_role = None

    async def _ban(self, target: Member, end_time: timedelta, reason: str):
        add_temp_ban_entry(target.id, end_time, target.guild.id)
        await target.ban(reason=reason)

    async def _mute(self, target: Member, end_time: timedelta, mute_type):
        add_temp_mute_entry(target.id, end_time, mute_type, target.guild.id)

        if mute_type == "text" or mute_type == "all":
            for channel in target.guild.text_channels:
                perms = channel.overwrites_for(target)
                perms.send_messages = False
                await channel.set_permissions(target, overwrite=perms)

        if mute_type == "voice" or mute_type == "all":
            for channel in target.guild.voice_channels:
                perms = channel.overwrites_for(target)
                perms.speak = False
                await channel.set_permissions(target, overwrite=perms)

    async def _assign_role(self, target: Member, end_time: timedelta, role: Role):
        add_temp_role_entry(target.id, end_time, role.id, target.guild.id)
        await target.add_roles(role)

    async def _wait_and_unban(self, target: Member = None, entry: list = None):
        assert target is not None or entry is not None
        end_date = datetime.utcnow()
        guild = None

        if target:
            _, end_date, _ = get_temp_ban_entry(target.id, target.guild.id)
            guild = target.guild
        elif entry:
            target_id, end_date, guild_id = entry
            guild = self.bot.get_guild(guild_id)
            target = (await guild.fetch_ban(Object(id=int(target_id)))).user

        if end_date > datetime.utcnow():
            delta_time = end_date - datetime.utcnow()
            await sleep(delta_time.total_seconds())

        try:
            if isinstance(target, User):
                await guild.unban(user=target, reason="Temp. ban ended")
            elif isinstance(target, Member):
                await target.unban(reason="Temp. ban ended")
        except NotFound:
            raise
        finally:
            delete_temp_ban_entry(target.id, guild.id)

    async def _wait_and_unmute(self, target: Member = None, entry: list = None):
        assert target is not None or entry is not None
        end_date = datetime.utcnow()
        guild = None
        mute_type = None

        if target:
            _, end_date, mute_type, _ = get_temp_mute_entry(target.id, target.guild.id)
            guild = target.guild
        elif entry:
            target_id, end_date, mute_type, guild_id = entry
            guild = self.bot.get_guild(guild_id)
            target = guild.get_member(user_id=target_id)

        if end_date > datetime.utcnow():
            delta_time = end_date - datetime.utcnow()
            await sleep(delta_time.total_seconds())

        if mute_type == "text" or mute_type == "all":
            for channel in guild.text_channels:
                perms = channel.overwrites_for(target)
                perms.send_messages = True
                await channel.set_permissions(target, overwrite=perms)

        if mute_type == "voice" or mute_type == "all":
            for channel in guild.voice_channels:
                perms = channel.overwrites_for(target)
                perms.speak = True
                await channel.set_permissions(target, overwrite=perms)

        await send_unmute_embeds(target)
        delete_temp_mute_entry(target.id, guild.id)

    async def _wait_and_remove_role(self, target: Member = None, entry: list = None):
        assert target is not None or entry is not None
        end_date = datetime.utcnow()
        guild = None
        role_id = None

        if target:
            _, end_date, role_id, _ = get_temp_role_entry(target.id, target.guild.id)
            guild = target.guild
        elif entry:
            target_id, end_date, role_id, guild_id = entry
            guild = self.bot.get_guild(guild_id)
            target = guild.get_member(user_id=target_id)

        if end_date > datetime.utcnow():
            delta_time = end_date - datetime.utcnow()
            await sleep(delta_time.total_seconds())

        role = guild.get_role(role_id=role_id)
        await target.remove_roles(role)
        delete_temp_role_entry(target.id, guild.id)

    async def _reload_temp_bans_waiting(self):
        if all_entries := get_all_temp_ban_entries():
            for entry in all_entries:
                await self._wait_and_unban(entry=entry)

    async def _reload_temp_mutes_waiting(self):
        if all_entries := get_all_temp_mute_entries():
            for entry in all_entries:
                await self._wait_and_unmute(entry=entry)

    async def _reload_temp_role_waiting(self):
        if all_entries := get_all_temp_role_entries():
            for entry in all_entries:
                await self._wait_and_remove_role(entry=entry)

    @command(name="temp_ban")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def temp_ban_user(self, ctx: Context, target: Member, time: TimeConverter(), *,
                            reason: Optional[str] = "No reason provided"):

        if not target:
            raise MissingRequiredArgument(target)

        if not time:
            raise MissingRequiredArgument(time)

        if ctx.guild.me.top_role.position > target.top_role.position \
                and not target.guild_permissions.administrator:
            link = await ctx.channel.create_invite(max_uses=1, unique=True)

            await send_temp_ban_embeds(target, time.__str__(), link, reason)
            await self._ban(target, time.get_end_time(), reason)

            # TODO remove next line
            await ctx.send(f"Banned {target.mention}", delete_after=10)

        else:
            raise MissingPermissions("Нельзя банить участника с более высокой ролью")

        await self._wait_and_unban(target=target)
        # TODO remove next line
        await ctx.send(f"Unbanned {target.mention}", delete_after=10)

    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    @command(name="mute")
    async def mute_user(self, ctx: Context, target: Member, time: TimeConverter(), mute_type: str = "all", *,
                        reason: Optional[str] = "No reason provided"):

        if not target:
            raise MissingRequiredArgument(target)

        if not mute_type:
            raise MissingRequiredArgument(target)

        if mute_type not in ["all", "text", "voice"]:
            raise BadArgument

        if ctx.guild.me.top_role.position > target.top_role.position \
                and not target.guild_permissions.administrator:
            await self._mute(target, time.get_end_time(), mute_type)
            await send_mute_embeds(target, time.__str__(), reason)

            # TODO remove next line
            await ctx.send(f"Muted {target.mention}", delete_after=10)

        else:
            raise MissingPermissions("Нельзя мутить участника с более высокой ролью")

        await self._wait_and_unmute(target=target)

    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    @command(name="unmute")
    async def unmute_user(self, ctx: Context, target: Member, unmute_type: str = "all"):

        if not target:
            raise MissingRequiredArgument(target)
        if not unmute_type:
            raise MissingRequiredArgument(unmute_type)

        if unmute_type not in ["all", "text", "voice"]:
            raise BadArgument

        if ctx.guild.me.top_role.position > target.top_role.position \
                and not target.guild_permissions.administrator:

            if unmute_type == "text" or unmute_type == "all":
                for channel in target.guild.text_channels:
                    perms = channel.overwrites_for(target)
                    perms.send_messages = True
                    await channel.set_permissions(target, overwrite=perms)

            if unmute_type == "voice" or unmute_type == "all":
                for channel in target.guild.voice_channels:
                    perms = channel.overwrites_for(target)
                    perms.speak = True
                    await channel.set_permissions(target, overwrite=perms)

                # TODO remove next line
                await ctx.send(f"Unmuted {target.mention}", delete_after=10)
            else:
                raise MissingPermissions("Нельзя анмутить участника с более высокой ролью")

    @command(name="ban")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def ban_user(self, ctx: Context, target: Member, *,  reason: Optional[str] = "No reason provided"):

        if not target:
            raise MissingRequiredArgument("Цель")

        if ctx.guild.me.top_role.position > target.top_role.position \
                and not target.guild_permissions.administrator:

            await send_ban_embeds(target, reason)
            await target.ban(reason=reason)

            # TODO remove next line
            await ctx.send(f"Banned {target.mention}", delete_after=10)
        else:
            raise MissingPermissions("Нельзя банить участника с более высокой ролью")

    @command(name="unban")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def unban_user(self, ctx: Context, target: BannedUser(), *,
                         reason: Optional[str] = "No reason provided"):
        if not target:
            raise MissingRequiredArgument("Цель")

        await ctx.guild.unban(target, reason=reason)
        # TODO remove next line
        await ctx.send(f"Unbanned {target.mention}", delete_after=10)

    @command(name="kick")
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick_user(self, ctx: Context, target: Member, *, reason: Optional[str] = "No reason provided"):

        if not target:
            raise MissingRequiredArgument("Цель")

        if ctx.guild.me.top_role.position > target.top_role.position \
                and not target.guild_permissions.administrator:

            link = await ctx.channel.create_invite(max_uses=1, unique=True)

            await send_kick_embeds(target, link, reason)
            await target.kick(reason=reason)

            # TODO remove next line
            await ctx.send(f"Kicked {target.mention}", delete_after=10)
        else:
            raise MissingPermissions("Нельзя кикать участника с более высокой ролью")

    @command(name="clear", aliases=['cls'])
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):

        if not amount:
            raise MissingRequiredArgument(amount)

        with ctx.channel.typing():
            await ctx.message.delete()
            await ctx.channel.purge(limit=amount)

    @bot_has_permissions(manage_roles=True, ban_members=True)
    @has_permissions(manage_roles=True, ban_members=True)
    @command(name="warn")
    async def warn_user(self, ctx: Context, target: Member, *, reason: Optional[str] = "No reason provided"):
        if not target:
            raise MissingRequiredArgument(target)

        update_warn_entry(target.id, target.guild.id, reason)
        await send_warn_embeds(target, reason)

        # TODO remove next line
        await ctx.send(f"Warned {target.mention}", delete_after=10)

        if (num_warns := get_warn_entry(target.id, target.guild.id)[1]) % NUM_WARNS_TO_TEMP_BAN == 0:

            await self.temp_ban_user(ctx, target,
                                     time=await TimeConverter().convert(ctx, arg=TIME_TO_TEMP_BAN),
                                     reason=f"Вы получили очередные {NUM_WARNS_TO_TEMP_BAN} "
                                            f"предупреждений и были забанены."
                                            f"Общее количево предупреждений: {num_warns}")

    @bot_has_permissions(manage_roles=True, ban_members=True)
    @has_permissions(manage_roles=True, ban_members=True)
    @command(name="unwarn")
    async def unwarn_user(self, ctx: Context, target: Member):
        if not target:
            raise MissingRequiredArgument(target)

        unwarn_entry(target.id, ctx.guild.id)

        # TODO remove next line
        await ctx.send(f"UnWarned {target.mention}", delete_after=10)

    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    @command(name="temp_role")
    async def assign_temp_role(self, ctx: Context, target: Member, role: Role, time: TimeConverter()):
        if not target:
            raise MissingRequiredArgument(target)
        if not role:
            raise MissingRequiredArgument(role)
        if not time:
            raise MissingRequiredArgument(time)

        await self._assign_role(target, time.get_end_time(), role)
        # TODO remove next line
        await ctx.send(f"Assign role {role.mention} to {target.mention}", delete_after=10)
        await self._wait_and_remove_role(target=target)

    @command(name="echo")
    async def echo(self, ctx: Context, *, phrase: str):
        if not phrase:
            raise MissingRequiredArgument(phrase)

        await ctx.message.delete()
        await ctx.send(phrase)

    @Cog.listener()
    async def on_ready(self):
        # remembers all temp-muted/temp-banned/temp-rolled users
        self.bot.loop.create_task(self._reload_temp_bans_waiting())
        self.bot.loop.create_task(self._reload_temp_mutes_waiting())
        self.bot.loop.create_task(self._reload_temp_role_waiting())


def setup(bot):
    bot.add_cog(Mod(bot))
