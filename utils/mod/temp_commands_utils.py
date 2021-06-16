from utils.db.moderation import get_all_temp_role_entries, get_all_temp_ban_entries, get_all_temp_mute_entries
from utils.db.moderation import delete_temp_role_entry, delete_temp_ban_entry, delete_temp_mute_entry
from utils.db.moderation import add_temp_role_entry, add_temp_ban_entry, add_temp_mute_entry
from utils.db.moderation import get_temp_role_entry, get_temp_ban_entry, get_temp_mute_entry
from utils.mod.mod_embeds import send_unmute_embeds
from discord import Member, Object, NotFound, User, Role
from datetime import datetime, timedelta
from asyncio import sleep


async def temp_ban_user(target: Member, end_time: timedelta, reason: str):
    add_temp_ban_entry(target.id, end_time, target.guild.id)
    await target.ban(reason=reason)


async def temp_mute_user(target: Member, end_time: timedelta, mute_type):
    add_temp_mute_entry(target.id, end_time, mute_type, target.guild.id)

    if mute_type in ["text", "all"]:
        for channel in target.guild.text_channels:
            perms = channel.overwrites_for(target)
            perms.send_messages = False
            await channel.set_permissions(target, overwrite=perms)

    if mute_type == "voice" or mute_type == "all":
        for channel in target.guild.voice_channels:
            perms = channel.overwrites_for(target)
            perms.speak = False
            await channel.set_permissions(target, overwrite=perms)


async def temp_role_user(target: Member, end_time: timedelta, role: Role):
    add_temp_role_entry(target.id, end_time, role.id, target.guild.id)
    await target.add_roles(role)


async def wait_and_unban(bot, target: Member = None, entry: list = None):
    assert target or entry
    end_date = datetime.utcnow()
    guild = None

    if target:
        if entry := get_temp_ban_entry(target.id, target.guild.id):
            _, _, end_date = entry
            guild = target.guild
        else:
            return

    elif entry:
        target_id, guild_id, end_date = entry
        guild = bot.get_guild(guild_id)
        target = (await guild.fetch_ban(Object(id=int(target_id)))).user

    if end_date > datetime.utcnow():
        delta_time = end_date - datetime.utcnow()
        await sleep(delta_time.total_seconds())

    if get_temp_ban_entry(target.id, guild.id):
        try:
            if isinstance(target, User):
                await guild.unban(user=target, reason="Temp. ban ended")
            elif isinstance(target, Member):
                await target.unban(reason="Temp. ban ended")
        except NotFound:
            raise
        finally:
            delete_temp_ban_entry(target.id, guild.id)


async def wait_and_unmute(bot, target: Member = None, entry: list = None):
    assert target or entry
    end_date = datetime.utcnow()
    guild = None
    mute_type = None

    if target:
        if entry := get_temp_mute_entry(target.id, target.guild.id):
            _, _, end_date, mute_type = entry
            guild = target.guild
        else:
            return

    elif entry:
        target_id, guild_id, end_date, mute_type = entry
        guild = bot.get_guild(guild_id)
        target = guild.get_member(user_id=target_id)

    if end_date > datetime.utcnow():
        delta_time = end_date - datetime.utcnow()
        await sleep(delta_time.total_seconds())

    # Check if user is still muted (wasn't unmuted manually)
    if get_temp_mute_entry(target.id, target.guild.id):
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


async def wait_and_remove_role(bot, target: Member = None, entry: list = None):
    assert target or entry
    end_date = datetime.utcnow()
    guild = None
    role_id = None

    if target:
        if entry := get_temp_role_entry(target.id, target.guild.id):
            _, _, end_date, role_id = entry
            guild = target.guild
        else:
            return

    elif entry:
        target_id, guild_id, end_date, role_id = entry
        guild = bot.get_guild(guild_id)
        target = guild.get_member(user_id=target_id)

    if end_date > datetime.utcnow():
        delta_time = end_date - datetime.utcnow()
        await sleep(delta_time.total_seconds())

    if get_temp_role_entry(target.id, target.guild.id):
        role = guild.get_role(role_id=role_id)
        await target.remove_roles(role)
        delete_temp_role_entry(target.id, guild.id)


async def reload_temp_bans_waiting(bot):
    if all_entries := get_all_temp_ban_entries():
        for entry in all_entries:
            await wait_and_unban(bot=bot, entry=entry)


async def reload_temp_mutes_waiting(bot):
    if all_entries := get_all_temp_mute_entries():
        for entry in all_entries:
            await wait_and_unmute(bot=bot, entry=entry)


async def reload_temp_role_waiting(bot):
    if all_entries := get_all_temp_role_entries():
        for entry in all_entries:
            await wait_and_remove_role(bot=bot, entry=entry)
