from config.config import TEMP_BAN_EMBEDS_DIR, BAN_EMBEDS_DIR, WARN_EMBEDS_DIR
from config.config import UNMUTE_EMBEDS_DIR, MUTE_EMBEDS_DIR, KICK_EMBEDS_DIR
from discord import Embed
from json import loads


def parse_embeds_json(json_file):
    embeds_json = loads(json_file)['embeds']

    for embed_json in embeds_json:
        embed = Embed().from_dict(embed_json)
        yield embed


async def send_temp_ban_embeds(user, ban_time, link, reason):
    with open(TEMP_BAN_EMBEDS_DIR, "r") as file:
        temp_ban_embeds = parse_embeds_json(file.read())

    for embed in temp_ban_embeds:
        if embed.description:
            embed.description = embed.description.format(time=ban_time, reason=reason, link=link)

        await user.send(embed=embed)


async def send_ban_embeds(user, reason):
    with open(BAN_EMBEDS_DIR, "r") as file:
        ban_embeds = parse_embeds_json(file.read())

    for embed in ban_embeds:
        if embed.description:
            embed.description = embed.description.format(reason=reason)

        await user.send(embed=embed)


async def send_warn_embeds(user, reason):
    with open(WARN_EMBEDS_DIR, "r") as file:
        warn_embeds = parse_embeds_json(file.read())

    for embed in warn_embeds:
        if embed.description:
            embed.description = embed.description.format(reason=reason)

        await user.send(embed=embed)


# noinspection PyUnusedLocal
async def send_kick_embeds(user, link, reason):
    with open(KICK_EMBEDS_DIR, "r") as file:
        kick_embeds = parse_embeds_json(file.read())

    for embed in kick_embeds:
        if embed.description:
            embed.description = embed.description.format(reason=reason)

        await user.send(embed=embed)


async def send_mute_embeds(user, mute_time, reason):
    with open(MUTE_EMBEDS_DIR, "r") as file:
        mute_embeds = parse_embeds_json(file.read())

    for embed in mute_embeds:
        if embed.description:
            embed.description = embed.description.format(time=mute_time, reason=reason)

        await user.send(embed=embed)


async def send_unmute_embeds(user):
    with open(UNMUTE_EMBEDS_DIR, "r") as file:
        unmute_embeds = parse_embeds_json(file.read())

    for embed in unmute_embeds:
        await user.send(embed=embed)
