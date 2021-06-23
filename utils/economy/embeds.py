from discord import Member, Embed, Guild

from config.economy.embeds_data import GET_MONEY_INFO_EMBEDS_PATH, SHOP_EMBEDS_PATH, WORK_LIST_EMBEDS_PATH, \
    CASINO_FAILURE_EMBEDS_PATH, CASINO_WIN_EMBEDS_PATH, TRANSACTION_EMBEDS_PATH, TOP10_USERS_EMBEDS_PATH
from config.economy.embeds_data import GOOD_WORK_RESULT_EMBEDS_PATH, BAD_WORK_RESULT_EMBEDS_PATH
from config.economy.work import WORK_LIST
from utils.common.utils import load_file
from utils.db.economy import get_money, get_all_shop_roles, get_top_10_users_by_economy, get_money_deposit


def get_money_info_embeds(bot, user: Member, guild: Guild):

    money = get_money(user.id, guild.id)
    deposit_money = get_money_deposit(user.id, guild.id)
    embed_dict = load_file(GET_MONEY_INFO_EMBEDS_PATH)

    money_embed = Embed().from_dict(embed_dict)
    money_embed.description = money_embed.description.format(user=user.mention,
                                                             money=money,
                                                             deposit_money=deposit_money,
                                                             symbol=bot.money_symbol)

    return money_embed


def get_shop_embeds(bot, guild: Guild):

    role_ids_and_costs = get_all_shop_roles(guild.id)

    embed_dict = load_file(SHOP_EMBEDS_PATH)
    shop_embed = Embed().from_dict(embed_dict)

    if not role_ids_and_costs:
        shop_embed.description = shop_embed.description.format(roles="Сожалеем, магазин пуст :С")
        return shop_embed

    roles = []
    for guild_id, role_id, costs in role_ids_and_costs:
        role = bot.guild.get_role(int(role_id))
        roles.append(f"Роль {role.mention} стоит `{costs}` {bot.money_symbol}")

    roles = "\n".join(roles)
    shop_embed.description = shop_embed.description.format(roles=roles)

    return shop_embed


def get_work_list_embeds(bot):

    embed_dict = load_file(WORK_LIST_EMBEDS_PATH)
    work_list_embed = Embed().from_dict(embed_dict)

    if not WORK_LIST:
        work_list_embed.description = work_list_embed.description.format(roles="Сожалеем, работы сейчас нет :С")
        return work_list_embed

    works = []
    for work_name, salary in WORK_LIST.items():
        works.append(f'Должность **"{work_name.title()}"**, оклад до `{salary}` {bot.money_symbol}')

    works = "\n".join(works)
    work_list_embed.description = work_list_embed.description.format(work_list=works)

    return work_list_embed


def good_work_result_embeds(bot, user: Member, money: int):

    embed_dict = load_file(GOOD_WORK_RESULT_EMBEDS_PATH)
    work_result_embed = Embed().from_dict(embed_dict)

    work_result_embed.description = work_result_embed.description.format(user=user.mention,
                                                                         money=money,
                                                                         symbol=bot.money_symbol)

    return work_result_embed


def bad_work_result_embeds(bot, user: Member, money: int):

    embed_dict = load_file(BAD_WORK_RESULT_EMBEDS_PATH)
    work_result_embed = Embed().from_dict(embed_dict)

    work_result_embed.description = work_result_embed.description.format(user=user.mention,
                                                                         money=money,
                                                                         symbol=bot.money_symbol)

    return work_result_embed


def win_embeds(bot, user, money):
    embed_dict = load_file(CASINO_WIN_EMBEDS_PATH)
    casino_win_embed = Embed().from_dict(embed_dict)

    casino_win_embed.description = casino_win_embed.description.format(user=user.mention,
                                                                       money=money,
                                                                       symbol=bot.money_symbol)

    return casino_win_embed


def failure_embeds(bot, user, money):
    embed_dict = load_file(CASINO_FAILURE_EMBEDS_PATH)
    casino_failure_embed = Embed().from_dict(embed_dict)

    casino_failure_embed.description = casino_failure_embed.description.format(user=user.mention,
                                                                               money=money,
                                                                               symbol=bot.money_symbol)

    return casino_failure_embed


def transaction_embeds(money_symbol, user, target, money):
    embed_dict = load_file(TRANSACTION_EMBEDS_PATH)
    transaction_embed = Embed().from_dict(embed_dict)

    transaction_embed.description = transaction_embed.description.format(user=user.mention,
                                                                         target=target.mention,
                                                                         money=money,
                                                                         symbol=money_symbol)

    return transaction_embed


async def get_top10_users_embeds(guild: Guild, money_symbol: str):
    top_users_list = get_top_10_users_by_economy()
    embed_dict = load_file(TOP10_USERS_EMBEDS_PATH)
    top10_users_embeds = Embed().from_dict(embed_dict)
    top10_users_embeds.description = top10_users_embeds.description.format(symbol=money_symbol)

    if top_users_list:
        for user_id, place, money in top_users_list:
            user = await guild.fetch_member(user_id)
            name = f"**{place} место**"
            value = f"**Пользователь {user.mention}.** Счет: {money}{money_symbol}"
            top10_users_embeds.add_field(name=name, value=value, inline=False)
    else:
        top10_users_embeds.add_field(name=f"Пользователи с {money_symbol} не найдены",
                                     value="Попробуйте начать зарабатывать внутрисерверную валюту",
                                     inline=False)

    return top10_users_embeds
