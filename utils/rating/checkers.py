from json import loads
from discord import Member, Guild, CategoryChannel
from discord.utils import get as discord_get

from utils.db.rating.clan_rating import get_clan_level
from utils.db.rating.rating import get_level
from config.rating.roles import roles_per_levels, MAX_LEVEL_ROLE_ID, clan_roles_per_levels, CLAN_MAX_LEVEL_ROLE_ID
from config.rating.points_counter import NUM_LEVELS_FOR_NEXT_ROLE
from config.rating.roles import NEW_LEVEL_ROLE_MESSAGE_TEXT


def load_message(path):
    with open(path, "r", encoding='utf=8') as file:
        text = loads(file.read())['text']

    return text


async def check_level_and_get_role(user: Member, guild: Guild, prev_level):
    level = get_level(user.id, guild.id)

    if not level:
        return

    if (level - prev_level) >= NUM_LEVELS_FOR_NEXT_ROLE:
        last_roled_level = NUM_LEVELS_FOR_NEXT_ROLE * (level // NUM_LEVELS_FOR_NEXT_ROLE)

        next_role_id = roles_per_levels.get(last_roled_level, MAX_LEVEL_ROLE_ID)
        next_role = discord_get(guild.roles, id=next_role_id)

        if next_role not in user.roles:
            prev_role_id = roles_per_levels.get(last_roled_level - NUM_LEVELS_FOR_NEXT_ROLE, None)

            if prev_role_id:
                prev_role = discord_get(guild.roles, id=prev_role_id)
                await user.remove_roles(prev_role)

            await user.add_roles(next_role)

            congrats_message_text = load_message(NEW_LEVEL_ROLE_MESSAGE_TEXT)
            await user.send(congrats_message_text.format(level=level))


async def check_clan_level_and_get_role(user: Member, guild: Guild, clan: CategoryChannel, prev_level):
    level = get_clan_level(user.id, clan.id)

    if not level:
        return

    if (level - prev_level) >= NUM_LEVELS_FOR_NEXT_ROLE:
        last_roled_level = NUM_LEVELS_FOR_NEXT_ROLE * (level // NUM_LEVELS_FOR_NEXT_ROLE)

        next_role_id = clan_roles_per_levels.get(last_roled_level, CLAN_MAX_LEVEL_ROLE_ID)
        next_role = discord_get(guild.roles, id=next_role_id)

        if next_role not in user.roles:
            prev_role_id = clan_roles_per_levels.get(last_roled_level - NUM_LEVELS_FOR_NEXT_ROLE, None)

            if prev_role_id:
                prev_role = discord_get(guild.roles, id=prev_role_id)
                await user.remove_roles(prev_role)

            await user.add_roles(next_role)

            congrats_message_text = load_message(NEW_LEVEL_ROLE_MESSAGE_TEXT)

            # TODO improve: send to clan's rating channel. Save clan's rating channel's id to db and load it here

            await user.send(congrats_message_text.format(level=level))
