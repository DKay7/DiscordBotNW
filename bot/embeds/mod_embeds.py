from json import loads
from discord import Embed
from config.config import TEMP_BAN_EMBEDS_DIR, BAN_EMBEDS_DIR, WARN_EMBEDS_DIR


def parse_embed_json(json_file):
    embeds_json = loads(json_file)['embeds']

    for embed_json in embeds_json:
        embed = Embed().from_dict(embed_json)
        yield embed


async def send_temp_ban_embed(user, duration, link, reason):
    with open(TEMP_BAN_EMBEDS_DIR, "r") as file:
        temp_ban_embeds = parse_embed_json(file.read())

    for embed in temp_ban_embeds:
        if embed.description:
            embed.description = embed.description.format(time=duration, reason=reason, link=link)

        await user.send(embed=embed)


async def send_ban_embed(user, reason):
    with open(BAN_EMBEDS_DIR, "r") as file:
        ban_embeds = parse_embed_json(file.read())

    for embed in ban_embeds:
        if embed.description:
            embed.description = embed.description.format(reason=reason)

        await user.send(embed=embed)


async def send_warn_embed(user, reason):
    with open(WARN_EMBEDS_DIR, "r") as file:
        warn_embeds = parse_embed_json(file.read())

    for embed in warn_embeds:
        if embed.description:
            embed.description = embed.description.format(reason=reason)

        await user.send(embed=embed)


# noinspection PyUnusedLocal
async def send_kick_embed(user, link, reason):
    pass


# noinspection PyUnusedLocal
async def send_mute_embeds(user, duration, reason):
    pass


# noinspection PyUnusedLocal
async def send_unmute_embeds(user, reason):
    pass
