from json import loads
from discord import Embed
from config.utilities_commands.embed_data import AVATAR_EMBED_PATH


def get_avatar_embeds(user):
    with open(AVATAR_EMBED_PATH, "r") as file:
        embed_dict = loads(file.read())

    avatar_urls = list()
    for avatar_format in ['webp', 'jpeg', 'jpg', 'png']:
        avatar_urls.append(f'[{avatar_format}]({user.avatar_url_as(size=1024, format=avatar_format)})')

    avatar_embed = Embed().from_dict(embed_dict)
    avatar_embed.title = avatar_embed.title.format(username=user.display_name)
    avatar_embed.set_image(url=user.avatar_url_as(size=1024))
    avatar_embed.description = avatar_embed.description.format(description=" | ".join(avatar_urls))

    return avatar_embed
