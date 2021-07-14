from config.mod.mod_config import NUM_WARNS_TO_TEMP_BAN, TIME_TO_TEMP_BAN
from utils.db.moderation import update_warn_entry, get_warn_entry, unwarn_entry
from utils.mod.temp_commands_utils import temp_ban_and_unban


async def warn_user_util(target, reason, bot, guild, channel, time_to_temp_ban=TIME_TO_TEMP_BAN, convert_time=True):
    update_warn_entry(target.id, target.guild.id, reason)

    if get_warn_entry(target.id, target.guild.id)[2] % NUM_WARNS_TO_TEMP_BAN == 0:
        await temp_ban_and_unban(target, reason, bot, guild, channel, time_to_temp_ban, convert_time)


async def unwarn_user_util(target, guild):
    unwarn_entry(target.id, guild.id)
