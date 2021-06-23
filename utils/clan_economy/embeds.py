from discord import Member, GroupChannel, Embed
from config.clan_economy.embeds_data import GET_CLAN_MONEY_INFO_EMBEDS_PATH, CLAN_SHOP_EMBEDS_PATH
from utils.common.utils import load_file
from utils.db.clan_economy import get_clan_money, get_all_clan_shop_roles


def get_clan_money_info_embeds(bot, user: Member, clan: GroupChannel):

    money = get_clan_money(user.id, clan.id)
    embed_dict = load_file(GET_CLAN_MONEY_INFO_EMBEDS_PATH)

    money_embed = Embed().from_dict(embed_dict)
    money_embed.description = money_embed.description.format(money=money,
                                                             user=user.mention,
                                                             clan=clan.name,
                                                             symbol=bot.money_symbol)

    return money_embed


def get_clan_shop_embeds(bot, clan: GroupChannel):

    role_ids_and_costs = get_all_clan_shop_roles(clan.id)

    embed_dict = load_file(CLAN_SHOP_EMBEDS_PATH)
    shop_embed = Embed().from_dict(embed_dict)
    shop_embed.title = shop_embed.title.format(clan=clan.name)

    if not role_ids_and_costs:
        shop_embed.description = shop_embed.description.format(roles="Сожалеем, магазин пуст :С")
        return shop_embed

    roles = []
    for clan_id, role_id, costs in role_ids_and_costs:
        role = bot.guild.get_role(role_id)
        roles.append(f"Роль {role.mention} в этом клане стоит `{costs}`{bot.money_symbol}")

    roles = "\n".join(roles)
    shop_embed.description = shop_embed.description.format(roles=roles)

    return shop_embed
