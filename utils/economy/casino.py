import asyncio
from random import choices
from typing import List

from discord import Embed, Member
from discord.ext.commands import Context

from config.economy.casino import NUM_ROWS, FRUITS, NUM_COLS, DEFAULT, WIN_FACTOR
from config.economy.embeds_data import CASINO_EMBEDS_PATH
from utils.common.utils import load_file
from utils.db.economy import withdraw_money, add_money
from utils.economy.embeds import failure_embeds, win_embeds


async def proceed_slot_machine(ctx: Context, bot, user: Member, bet: int):
    withdraw_money(user.id, ctx.guild.id, bet)

    embed_dict = load_file(CASINO_EMBEDS_PATH)

    table = [[DEFAULT for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
    embed = make_str_table(table, embed_dict)
    message = await ctx.send(embed=embed)

    for column_index in range(NUM_COLS):
        await asyncio.sleep(1)
        new_column = choices(FRUITS, k=NUM_ROWS)

        for row_index in range(NUM_ROWS):
            table[row_index][column_index] = new_column[row_index]

        embed = make_str_table(table, embed_dict)
        await message.edit(embed=embed)

    win = False
    for row in table:
        if len(set(row)) == 1:
            win = True

    if win:
        add_money(user.id, ctx.guild.id, bet * WIN_FACTOR)
        win_embed = win_embeds(bot, user, bet * WIN_FACTOR)
        await ctx.send(embed=win_embed)
    else:
        failure_embed = failure_embeds(bot, user, bet)
        await ctx.send(embed=failure_embed)

    return win


def make_str_table(table: List[List[str]], embed_dict):
    flatten = list(map(lambda inner_list: "|".join(inner_list), table))
    str_rows = "\n".join(flatten)

    embed_pattern = Embed().from_dict(embed_dict)
    embed_pattern.description = embed_pattern.description.format(fruits=str_rows)

    return embed_pattern
