from utils.mod_utils.temp_commands_utils import temp_ban_user, temp_mute_user, temp_role_user
from utils.mod_utils.temp_commands_utils import wait_and_unban, wait_and_unmute
from utils.mod_utils.temp_commands_utils import reload_temp_mutes_waiting, reload_temp_role_waiting
from utils.mod_utils.temp_commands_utils import wait_and_remove_role, reload_temp_bans_waiting
from utils.db.db_mod_utils import update_warn_entry, get_warn_entry, unwarn_entry
from utils.db.db_mod_utils import delete_temp_mute_entry, delete_temp_ban_entry
from discord.ext.commands import Cog, Context, command, bot_has_permissions, has_permissions, MissingRequiredArgument
from bot.embeds.mod_embeds import send_temp_ban_embeds, send_ban_embeds,  send_kick_embeds
from config.mod_config import NUM_WARNS_TO_TEMP_BAN, TIME_TO_TEMP_BAN
from utils.mod_utils.data_converters import BannedUser, TimeConverter
from bot.embeds.mod_embeds import send_mute_embeds, send_warn_embeds
from discord.ext.commands import BadArgument, MissingPermissions
from bot.embeds.mod_embeds import send_unmute_embeds
from discord import Member, Role
from typing import Optional


class Mod(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.text_mute_role = None
        self.voice_mute_role = None

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
            await temp_ban_user(target, time.get_end_time(), reason)

            # TODO remove next line
            await ctx.send(f"Banned {target.mention}", delete_after=10)

        else:
            raise MissingPermissions("Нельзя банить участника с более высокой ролью")

        await wait_and_unban(bot=self.bot, target=target)
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
            await temp_mute_user(target, time.get_end_time(), mute_type)
            await send_mute_embeds(target, time.__str__(), reason)

            # TODO remove next line
            await ctx.send(f"Muted {target.mention}", delete_after=10)

        else:
            raise MissingPermissions("Нельзя мутить участника с более высокой ролью")

        await wait_and_unmute(bot=self.bot, target=target)

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
                delete_temp_mute_entry(target.id, ctx.guild.id)
                await send_unmute_embeds(target)
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
        delete_temp_ban_entry(target.id, ctx.guild.id)

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

        if (num_warns := get_warn_entry(target.id, target.guild.id)[2]) % NUM_WARNS_TO_TEMP_BAN == 0:

            await self.temp_ban_user(ctx, target,
                                     time=await TimeConverter().convert(ctx, arg=TIME_TO_TEMP_BAN),
                                     reason=f"Вы получили очередные {NUM_WARNS_TO_TEMP_BAN} "
                                            f"предупреждений и были забанены."
                                            f"Общее количество предупреждений: {num_warns}")

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

        await temp_role_user(target, time.get_end_time(), role)
        # TODO remove next line
        await ctx.send(f"Assign role {role.mention} to {target.mention}", delete_after=10)
        await wait_and_remove_role(bot=self.bot, target=target)

    @command(name="echo")
    async def echo(self, ctx: Context, *, phrase: str):
        if not phrase:
            raise MissingRequiredArgument(phrase)

        await ctx.message.delete()
        await ctx.send(phrase)

    @Cog.listener()
    async def on_ready(self):
        # remembers all temp-muted/temp-banned/temp-rolled users
        self.bot.loop.create_task(reload_temp_bans_waiting(self.bot))
        self.bot.loop.create_task(reload_temp_mutes_waiting(self.bot))
        self.bot.loop.create_task(reload_temp_role_waiting(self.bot))


def setup(bot):
    bot.add_cog(Mod(bot))
