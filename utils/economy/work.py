import asyncio
from random import choices

from discord import Member, Guild
from config.economy.work import WORK_LIST, SLEEP_TIME, BAD_WORK_CHANCE
from utils.db.economy import add_money


async def work(guild: Guild, user: Member, work_name: str):
    work_name = work_name.lower()

    if work_name not in WORK_LIST.keys():
        return False

    max_money = WORK_LIST[work_name]

    money_range = list(range(-max_money, max_money+1))
    weights = [1 if money <= 0 else (1 / BAD_WORK_CHANCE) - 1 for money in money_range]
    result_money = choices(money_range, weights=weights)[0]

    await asyncio.sleep(SLEEP_TIME)

    add_money(user.id, guild.id, result_money)

    return result_money
