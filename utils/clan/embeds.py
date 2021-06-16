from config.clan.embeds import CLAN_LEADER_OFFER_EMBEDS_PATH, CLAN_DEP_LEADER_OFFER_EMBEDS_PATH, DUEL_ASK_EMBEDS_PATH
from config.clan.embeds import CLAN_MEMBER_OFFER_EMBEDS_PATH, TOP10_CLAN_EMBEDS_PATH, DUEL_RESULT_EMBEDS_PATH
from config.clan.embeds import DUEL_DENY_EMBEDS_PATH

from config.clan.reactions_path import CLAN_LEADER_OFFER_REACTIONS_PATH, CLAN_DEP_LEADER_OFFER_REACTIONS_PATH
from config.clan.reactions_path import CLAN_MEMBER_OFFER_REACTIONS_PATH, DUEL_ASK_REACTIONS_PATH
from discord import Embed
from utils.common.utils import load_file
from utils.db.clans import get_top_10_clans


def get_offer_embeds_and_reactions(type_, clan_name=""):
    assert type_ in ["leader", "dep_leader", "member"]

    path = ""
    reactions_path = ""
    if type_ == "leader":
        path = CLAN_LEADER_OFFER_EMBEDS_PATH
        reactions_path = CLAN_LEADER_OFFER_REACTIONS_PATH
    elif type_ == "dep_leader":
        path = CLAN_DEP_LEADER_OFFER_EMBEDS_PATH
        reactions_path = CLAN_DEP_LEADER_OFFER_REACTIONS_PATH
    elif type_ == "member":
        path = CLAN_MEMBER_OFFER_EMBEDS_PATH
        reactions_path = CLAN_MEMBER_OFFER_REACTIONS_PATH

    reactions = load_file(reactions_path)
    embed_dict = load_file(path)
    offer_embed = Embed().from_dict(embed_dict)

    offer_embed.description = offer_embed.description.format(clan_name=clan_name)

    return offer_embed, reactions


def get_top10_clans_embed():
    top_clans_list = get_top_10_clans()
    embed_dict = load_file(TOP10_CLAN_EMBEDS_PATH)
    top10_clans_embed = Embed().from_dict(embed_dict)

    if top_clans_list:
        for clan_name, number, win_points in top_clans_list:
            name = f"**{number} место**"
            value = f"**Клан `{clan_name}`.** Счет: {win_points}"
            top10_clans_embed.add_field(name=name, value=value, inline=False)
    else:
        top10_clans_embed.add_field(name="Кланы не найдены",
                                    value="Попробуйте создать свой первый клан", inline=False)

    return top10_clans_embed


def get_duel_ask_embeds(user, opponent):
    embed_dict = load_file(DUEL_ASK_EMBEDS_PATH)
    reactions = load_file(DUEL_ASK_REACTIONS_PATH)

    duel_asks_embed = Embed().from_dict(embed_dict)

    duel_asks_embed.description = duel_asks_embed.description.format(user=user.mention,
                                                                     opponent=opponent.mention)

    return duel_asks_embed, reactions


def get_duel_result_embed(user, opponent, winner):
    embed_dict = load_file(DUEL_RESULT_EMBEDS_PATH)

    duel_result_embed = Embed().from_dict(embed_dict)

    duel_result_embed.description = duel_result_embed.description.format(user=user.mention,
                                                                         opponent=opponent.mention,
                                                                         winner=winner.mention)

    return duel_result_embed


def get_duel_deny_embed(user, opponent):
    embed_dict = load_file(DUEL_DENY_EMBEDS_PATH)

    duel_result_embed = Embed().from_dict(embed_dict)

    duel_result_embed.description = duel_result_embed.description.format(user=user.mention,
                                                                         opponent=opponent.mention)

    return duel_result_embed
