from discord import Member, GroupChannel, Embed
from config.clan_economy.embeds_data import GET_MONEY_INFO_EMBEDS_PATH, CLAN_SHOP_EMBEDS_PATH
from utils.common.utils import load_file
from utils.db.clan_economy import get_money, get_shop_roles


def get_money_info_embeds(user: Member, clan: GroupChannel):

    money = get_money(user.id, clan.id)
    embed_dict = load_file(GET_MONEY_INFO_EMBEDS_PATH)

    money_embed = Embed().from_dict(embed_dict)
    money_embed.description = money_embed.description.format(money=money,
                                                             user=user.mention,
                                                             clan=clan.name)

    return money_embed


def get_shop_embeds(bot, clan: GroupChannel):

    role_ids_and_costs = get_shop_roles(clan.id)

    embed_dict = load_file(CLAN_SHOP_EMBEDS_PATH)
    shop_embed = Embed().from_dict(embed_dict)
    shop_embed.title = shop_embed.title.format(clan=clan.name)

    if not role_ids_and_costs:
        shop_embed.description = shop_embed.description.format(roles="Сожалеем, магазин пуст :С")
        return shop_embed

    roles = []
    for role_id, costs in role_ids_and_costs.items():
        role = bot.guild.get_role(int(role_id))
        roles.append(f"Роль {role.mention} в этом клане стоит `{costs}` кредитов")

    roles = "\n".join(roles)
    shop_embed.description = shop_embed.description.format(roles=roles)

    return shop_embed
