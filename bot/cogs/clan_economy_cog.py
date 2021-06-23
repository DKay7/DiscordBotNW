from discord.ext.commands import Cog, command, Context, cooldown, MissingRequiredArgument, BucketType
from discord.ext.commands.core import guild_only
from utils.db.clan_economy import add_clan_money, add_clan_shop_roles, delete_clan_shop_roles
from utils.db.clan_economy import get_clan_shop_role_cost
from utils.db.clan_economy import get_clan_money, withdraw_clan_money
from utils.common.checkers import check_user_in_clan, check_admin
from discord import Member, Role
from config.clan_economy.config import DAILY_MONEY_AMOUNT
from utils.clan_economy.embeds import get_clan_money_info_embeds, get_clan_shop_embeds


class ClanEconomyCog(Cog):
    def __init__(self, bot):
        self.bot = bot
    # TODO rewrite roles db storage architecture!!

    @guild_only()
    @cooldown(per=60*60*24, rate=1, type=BucketType.user)
    @command(name="clan_daily")
    async def get_daily(self, ctx: Context):
        if check_user_in_clan(ctx.author, ctx.channel.category):
            add_clan_money(ctx.author.id, ctx.channel.category.id, DAILY_MONEY_AMOUNT)
            await ctx.send(f"{ctx.author.mention} получил ежедневную выплату", delete_after=10)
        else:
            await ctx.send(f"Вы не состоите в клане, либо запускаете команду не в канале клана", delete_after=10)

    @guild_only()
    @command(name="check_clan_money")
    async def check_clan_money(self, ctx: Context):
        if check_user_in_clan(ctx.author, ctx.channel.category):
            money_embed = get_clan_money_info_embeds(self.bot, ctx.author, ctx.channel.category)
            await ctx.send(embed=money_embed)
        else:
            await ctx.send(f"Вы не состоите в клане, либо запускаете команду не в канале клана", delete_after=10)

    @guild_only()
    @command(name="show_clan_shop")
    async def show_clan_shop(self, ctx: Context):
        if check_user_in_clan(ctx.author, ctx.channel.category):
            shop_embed = get_clan_shop_embeds(self.bot, ctx.channel.category)
            await ctx.send(embed=shop_embed)
        else:
            await ctx.send(f"Вы не состоите в клане, либо запускаете команду не в канале клана", delete_after=10)

    @guild_only()
    @command(name="buy_clan_shop_role")
    async def buy_clan_shop_role(self, ctx: Context, role: Role):
        if check_user_in_clan(ctx.author, ctx.channel.category):
            role_cost = get_clan_shop_role_cost(ctx.channel.category.id, role.id)

            if not role_cost:
                await ctx.send(f"В магазине клана нет такой роли", delete_after=10)
                return

            money = get_clan_money(ctx.author.id, ctx.channel.category.id)

            if money - role_cost >= 0:
                withdraw_clan_money(ctx.channel.category.id, ctx.author.id, role_cost)
                await ctx.author.add_roles(role, reason=f"Покупка роли в магазине клана "
                                                        f"{ctx.channel.category.name}")
                await ctx.send(f"Спасибо за покупку!", delete_after=10)
            else:
                await ctx.send(f"Недостаточно средств на счету", delete_after=10)
                return
        else:
            await ctx.send(f"Вы не состоите в клане, либо запускаете команду не в канале клана", delete_after=10)
            return

    @guild_only()
    @check_admin()
    @command(name="add_role_to_clan_shop")
    async def add_role_to_clan_shop(self, ctx: Context, role: Role, cost: int):
        if check_user_in_clan(ctx.author, ctx.channel.category):
            add_clan_shop_roles(ctx.channel.category.id, role.id, cost)
            await ctx.send(f"В магазин клана была добавлена роль {role.mention}", delete_after=10)

        else:
            await ctx.send(f"Вы не состоите в клане, либо запускаете команду не в канале клана", delete_after=10)

    @guild_only()
    @check_admin()
    @command(name="delete_role_from_clan_shop")
    async def delete_role_from_clan_shop(self, ctx: Context, role: Role):
        if check_user_in_clan(ctx.author, ctx.channel.category):
            delete_clan_shop_roles(ctx.channel.category.id, role.id)
            await ctx.send(f"Из магазина клана была удалена роль {role.mention}", delete_after=10)

        else:
            await ctx.send(f"Вы не состоите в клане, либо запускаете команду не в канале клана", delete_after=10)

    @guild_only()
    @check_admin()
    @command(name="set_clan_money")
    async def set_money(self, ctx: Context, user: Member, money: int):
        if not user:
            MissingRequiredArgument(user)
            return

        if not money:
            MissingRequiredArgument(money)
            return

        if check_user_in_clan(user, ctx.channel.category):
            add_clan_money(user.id, ctx.channel.category.id, money)

            if money > 0:
                await ctx.send(f"{user.mention} получил выплату от администратора в размере {money}", delete_after=10)
            elif money < 0:
                await ctx.send(f"{user.mention} был оштрафован администратором на сумму {money}", delete_after=10)
        else:
            await ctx.send(f"Пользователь {user.mention} не состоит в клане, "
                           f"либо вы запускаете команду не в канале клана", delete_after=10)


def setup(bot):
    bot.add_cog(ClanEconomyCog(bot))
