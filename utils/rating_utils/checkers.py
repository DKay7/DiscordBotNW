from json import loads
from discord import Member, Guild
from discord.utils import get as discord_get
from utils.db.db_rating_utils import get_level
from config.rating_config import NUM_LEVELS_FOR_NEXT_ROLE, roles_per_levels, MAX_LEVEL_ROLE_ID
from config.rating_config import NEW_LEVEL_ROLE_MESSAGE_TEXT


def load_message(path):
    with open(path, "r", encoding='utf=8') as file:
        text = loads(file.read())['text']

    return text


async def check_level_and_get_role(user: Member, guild: Guild):
    level = get_level(user.id, guild.id)

    if not level:
        return

    if level % NUM_LEVELS_FOR_NEXT_ROLE == 0 and level != 0:
        next_role_id = roles_per_levels.get(level, MAX_LEVEL_ROLE_ID)
        current_role_id = roles_per_levels.get(level - NUM_LEVELS_FOR_NEXT_ROLE, None)

        if current_role_id:
            current_role = discord_get(guild.roles, id=current_role_id)
            await user.remove_roles(current_role)

        next_role = discord_get(guild.roles, id=next_role_id)
        await user.add_roles(next_role)

        congrats_message_text = load_message(NEW_LEVEL_ROLE_MESSAGE_TEXT)
        await user.send(congrats_message_text.format(level=level))
