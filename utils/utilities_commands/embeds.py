from utils.common.utils import load_file
from discord import Embed
from config.utilities_commands.embed_data import AVATAR_EMBED_PATH, UTILITIES_EMBEDS_PATH, \
    MARRIAGES_CONFIRM_EMBEDS_PATH, MARRIAGES_DENY_EMBEDS_PATH, MARRIAGES_ASK_EMBEDS_PATH, SEX_DENY_EMBEDS_PATH,\
    SEX_ASK_EMBEDS_PATH, SEX_CONFIRM_EMBEDS_PATH
from utils.rating.progress_bar import get_stat_for_user


def get_avatar_embeds(user):
    embed_dict = load_file(AVATAR_EMBED_PATH)

    avatar_urls = list()
    for avatar_format in ['webp', 'jpeg', 'jpg', 'png']:
        avatar_urls.append(f'[{avatar_format}]({user.avatar_url_as(size=1024, format=avatar_format)})')

    avatar_embed = Embed().from_dict(embed_dict)
    avatar_embed.title = avatar_embed.title.format(username=user.display_name)
    avatar_embed.set_image(url=user.avatar_url_as(size=1024))
    avatar_embed.description = avatar_embed.description.format(description=" | ".join(avatar_urls))

    return avatar_embed


def get_utilities_embeds(description, gif_link):
    embed_dict = load_file(UTILITIES_EMBEDS_PATH)

    avatar_embed = Embed().from_dict(embed_dict)
    avatar_embed.set_image(url=gif_link)
    avatar_embed.description = avatar_embed.description.format(description=description)

    return avatar_embed


def get_marriages_embeds(user, target, type_=None):
    assert type_ in ["ask", "confirm", "deny"]

    path = ""

    if type_ == "ask":
        path = MARRIAGES_ASK_EMBEDS_PATH
    elif type_ == "confirm":
        path = MARRIAGES_CONFIRM_EMBEDS_PATH
    elif type_ == "deny":
        path = MARRIAGES_DENY_EMBEDS_PATH

    embed_dict = load_file(path)
    marriage_embed = Embed().from_dict(embed_dict)
    marriage_embed.description = marriage_embed.description.format(username=user.mention,
                                                                   target=target.mention)

    return marriage_embed


def get_sex_embeds(user, target, type_=None):
    assert type_ in ["ask", "confirm", "deny"]

    path = ""

    if type_ == "ask":
        path = SEX_ASK_EMBEDS_PATH
    elif type_ == "confirm":
        path = SEX_CONFIRM_EMBEDS_PATH
    elif type_ == "deny":
        path = SEX_DENY_EMBEDS_PATH

    embed_dict = load_file(path)
    sex_embed = Embed().from_dict(embed_dict)
    sex_embed.description = sex_embed.description.format(username=user.mention,
                                                         target=target.mention)

    return sex_embed


def get_user_info_embeds(user, guild):
    embed = Embed(title=f"Информация о пользователе {user.display_name}",
                  color=user.color)
    embed.set_thumbnail(url=user.avatar_url)

    rating, total_rating, level, position = get_stat_for_user(user, guild)

    fields = [("Id", f"`{user.id}`", False), ("Имя", f"`{user.name}`", True),
              ("Имя на сервере", f"`{user.display_name}`", True), ("Дискриминатор", f"`{user.discriminator}`", True),
              ("Статус", str(user.status).title(), False),
              ("Рейтинг", f"`#{position}`", True), ("Уровень", str(level), True),
              ("Опыт", f"`{rating}/{total_rating}`", True),
              ("Присоединился к серверу", user.joined_at, True), ("Присоединился к Discord", user.created_at, True)]

    roles = [role.mention for role in user.roles]
    fields.append((f"Роли ({len(roles)}):", " ".join(roles), False))

    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)

    return embed


def get_server_info_embeds(guild):
    embed = Embed(title=f"Информация о сервере {guild.name}",
                  color=guild.owner.color)
    embed.set_thumbnail(url=guild.icon_url)

    fields = [("Id", f"`{guild.id}`", True), ("Владелец", f"`{guild.owner}`", True),
              ("Участников", f"`{len(guild.members)}`", True),
              ("Текстовых каналов", f"`{len(guild.text_channels)}`", True),
              ("Голосовых каналов", f"`{len(guild.voice_channels)}`", True),
              ("Регион", f"`{guild.region}`", True), ("Уровень нитро", f"`{guild.premium_tier}`", True),
              ("Нитро бустеров", f"`{guild.premium_subscription_count}`", True)]

    emojis = [str(emoji) for emoji in guild.emojis[:25]]
    features = [f"`{feature}`" for feature in guild.features]

    if emojis:
        if len(emojis) != len(guild.emojis):
            emojis.append("`и другие...`")

        fields.append((f"Емоджи ({len(guild.emojis)}):", " ".join(emojis), False))
    if features:
        fields.append((f"Улучшения ({len(guild.features)}):", " ".join(features), False))

    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)

    return embed
