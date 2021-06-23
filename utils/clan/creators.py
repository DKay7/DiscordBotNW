from config.clan.patterns import user_types, channels
from config.clan.roles import CLAN_LEADER_ROLE, CLAN_MEMBER_ROLE, CLAN_DEP_ROLE
from config.clan.patterns import CLAN_CHANNELS_PERMS_ROLES_PATTERN
from utils.clan.getters_and_loaders import get_colour
from utils.common.utils import load_file
from discord import Guild, Permissions, PermissionOverwrite
from utils.db.clans import add_clan_to_db


async def create_clan_roles(guild: Guild, clan_name: str):
    leader_role = load_file(CLAN_LEADER_ROLE)
    deputy_leader_role = load_file(CLAN_DEP_ROLE)
    clan_member_role = load_file(CLAN_MEMBER_ROLE)

    leader_role_name = leader_role["name"].format(clan_name=clan_name)
    deputy_leader_role_name = deputy_leader_role["name"].format(clan_name=clan_name)
    clan_member_role_name = clan_member_role["name"].format(clan_name=clan_name)

    leader_role_colour = get_colour(leader_role, clan_name)
    deputy_leader_role_colour = get_colour(deputy_leader_role, clan_name)
    clan_member_role_colour = get_colour(clan_member_role, clan_name)

    leader_role_perms = Permissions(**leader_role["permissions"])
    deputy_leader_role_perms = Permissions(**deputy_leader_role["permissions"])
    clan_member_role_perms = Permissions(**clan_member_role["permissions"])

    leader_role = await guild.create_role(name=leader_role_name,
                                          colour=leader_role_colour,
                                          permissions=leader_role_perms)
    dep_role = await guild.create_role(name=deputy_leader_role_name,
                                       colour=deputy_leader_role_colour,
                                       permissions=deputy_leader_role_perms)
    member_role = await guild.create_role(name=clan_member_role_name,
                                          colour=clan_member_role_colour,
                                          permissions=clan_member_role_perms)

    return tuple((leader_role, dep_role, member_role))


async def create_clan_channels(guild: Guild, clan_roles: tuple, clan_name: str):
    assert len(clan_roles) == len(user_types)
    perms_overwrites = {guild.default_role: PermissionOverwrite(read_messages=False)}
    clan_category = await guild.create_category(f"Clan {clan_name}", overwrites=perms_overwrites)

    add_clan_to_db(clan_name=clan_name, group_channel_id=clan_category.id, clan_roles=clan_roles)

    for channel_key, channel in channels.items():
        for index, user_type in enumerate(user_types.values()):
            perms = load_file(CLAN_CHANNELS_PERMS_ROLES_PATTERN.format(user_type=user_type, channel_type=channel))

            perms_overwrites.update({clan_roles[index]: PermissionOverwrite(**perms)})

        if "voice" in channel_key:
            await guild.create_voice_channel(f"{channel}_{clan_name}",
                                             overwrites=perms_overwrites,
                                             category=clan_category)
        else:
            await guild.create_text_channel(f"{channel}_{clan_name}",
                                            overwrites=perms_overwrites,
                                            category=clan_category)
