from config.automoderation.embed_pathes import UPPERCASE_WARN_EMBEDS_PATH, EMOJI_WARN_EMBEDS_PATH
from config.automoderation.embed_pathes import MENTION_WARN_EMBEDS_PATH, SIMILARITY_WARN_EMBEDS_PATH
from config.automoderation.embed_pathes import SWEAR_WARN_EMBEDS_PATH, URL_WARN_EMBEDS_PATH
from discord import Member, Embed
from utils.common.utils import load_file


def get_emoji_warn_embeds(user: Member):
    embed_dict = load_file(EMOJI_WARN_EMBEDS_PATH)
    emoji_warn_embed = Embed().from_dict(embed_dict)

    emoji_warn_embed.description = emoji_warn_embed.description.format(user=user.mention)

    return emoji_warn_embed


def get_mention_warn_embeds(user: Member):
    embed_dict = load_file(MENTION_WARN_EMBEDS_PATH)
    mention_warn_embed = Embed().from_dict(embed_dict)

    mention_warn_embed.description = mention_warn_embed.description.format(user=user.mention)

    return mention_warn_embed


def get_swear_warn_embeds(user: Member):
    embed_dict = load_file(SWEAR_WARN_EMBEDS_PATH)
    swear_warn_embed = Embed().from_dict(embed_dict)

    swear_warn_embed.description = swear_warn_embed.description.format(user=user.mention)

    return swear_warn_embed


def get_url_warn_embeds(user: Member):
    embed_dict = load_file(URL_WARN_EMBEDS_PATH)
    url_warn_embed = Embed().from_dict(embed_dict)

    url_warn_embed.description = url_warn_embed.description.format(user=user.mention)

    return url_warn_embed


def get_uppercase_warn_embeds(user: Member):
    embed_dict = load_file(UPPERCASE_WARN_EMBEDS_PATH)
    uppercase_warn_embed = Embed().from_dict(embed_dict)

    uppercase_warn_embed.description = uppercase_warn_embed.description.format(user=user.mention)

    return uppercase_warn_embed


def get_similarity_warn_embeds(user: Member):
    embed_dict = load_file(SIMILARITY_WARN_EMBEDS_PATH)
    similarity_warn_embed = Embed().from_dict(embed_dict)

    similarity_warn_embed.description = similarity_warn_embed.description.format(user=user.mention)

    return similarity_warn_embed
