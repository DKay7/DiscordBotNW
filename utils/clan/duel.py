from utils.db.clan_economy import get_clan_money, withdraw_clan_money, add_clan_money
from random import choice
from utils.clan.embeds import get_duel_result_embed, get_duel_deny_embed
from utils.db.clans import delete_duel_response


async def proceed_duel(user, opponent, bet, channel):
    clan = channel.category
    money_opponent = get_clan_money(opponent.id, clan.id)

    if money_opponent - bet < 0:
        await channel.send(f"У вас недостаточно денег, чтобы принять ставку соперника")
        return

    withdraw_clan_money(opponent.id, clan.id, bet)

    winner = choice([user, opponent])
    add_clan_money(winner.id, clan.id, bet * 2)

    result_embed = get_duel_result_embed(user, opponent, winner)

    await channel.send(embed=result_embed)


async def deny_duel(user, opponent, bet, channel):
    delete_duel_response(user.id, opponent.id)
    add_clan_money(user.id, channel.category.id, bet)

    deny_embed = get_duel_deny_embed(user, opponent)

    await channel.send(embed=deny_embed)
