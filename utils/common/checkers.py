from discord import Member, GroupChannel
from discord.ext.commands import check

from config.bot.bot_config import ADMIN_ROLE_IDS
from utils.db.clans import get_clan_role_ids


def check_user_in_clan(user: Member, clan: GroupChannel):
    if clan and user:
        clan_role_ids = get_clan_role_ids(clan.id)

        if user.roles and clan_role_ids:
            return bool(set(clan_role_ids) & set(map(lambda role: role.id, user.roles)))
        else:
            return False
    else:
        return False


def check_admin():
    def predicate(ctx):
        return set(ADMIN_ROLE_IDS) & set(map(lambda role: role.id, ctx.author.roles))

    return check(predicate)
