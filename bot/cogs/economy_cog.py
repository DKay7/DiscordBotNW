from discord.ext.commands import Cog, command, Context, cooldown, MissingRequiredArgument, BucketType
from discord.ext.commands.core import guild_only

from utils.common.checkers import check_admin
from discord import Member, Role
from config.clan_economy.config import DAILY_MONEY_AMOUNT

from utils.db.economy import add_money, get_shop_role_cost, get_money, withdraw_money, add_shop_roles, \
    delete_shop_roles, add_money_symbol, reset_money, delete_user_from_economy, get_money_deposit, add_money_deposit, \
    withdraw_money_deposit

from utils.economy.casino import proceed_slot_machine

from utils.economy.embeds import get_shop_embeds, get_money_info_embeds, get_work_list_embeds, \
    good_work_result_embeds, transaction_embeds, get_top10_users_embeds

from utils.economy.embeds import bad_work_result_embeds
from utils.economy.work import work


class EconomyCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @guild_only()
    @cooldown(per=60*60*24, rate=1, type=BucketType.user)
    @command(name="daily")
    async def get_daily(self, ctx: Context):
        add_money(ctx.author.id, ctx.guild.id, DAILY_MONEY_AMOUNT)
        await ctx.send(f"{ctx.author.mention} получил ежедневную выплату", delete_after=10)

    @guild_only()
    @command(name="check_money")
    async def check_money(self, ctx: Context):
        money_embed = get_money_info_embeds(self.bot, ctx.author, ctx.guild)
        await ctx.send(embed=money_embed)

    @guild_only()
    @command(name="show_shop")
    async def show_shop(self, ctx: Context):
        shop_embed = get_shop_embeds(self.bot, ctx.guild)
        await ctx.send(embed=shop_embed)

    @guild_only()
    @command(name="buy_shop_role")
    async def buy_shop_role(self, ctx: Context, role: Role):
        role_cost = get_shop_role_cost(ctx.guild.id, role.id)

        if not role_cost:
            await ctx.send(f"В магазине сервера нет такой роли", delete_after=10)
            return

        if role in ctx.author.roles:
            await ctx.send(f"У вас уже есть такая роль", delete_after=10)
            return

        money = get_money(ctx.author.id, ctx.guild.id)

        if money - role_cost >= 0:
            withdraw_money(ctx.author.id, ctx.guild.id, role_cost)
            await ctx.author.add_roles(role, reason=f"Покупка роли в магазине сервера")
            await ctx.send(f"Спасибо за покупку!", delete_after=10)
        else:
            await ctx.send(f"Недостаточно средств на счету", delete_after=10)
            return

    @guild_only()
    @check_admin()
    @command(name="add_role_to_shop")
    async def add_role_to_shop(self, ctx: Context, role: Role, cost: int):
        add_shop_roles(ctx.guild.id, role.id, cost)
        await ctx.send(f"В магазин сервера была добавлена роль {role.mention}", delete_after=10)

    @guild_only()
    @check_admin()
    @command(name="delete_role_from_shop")
    async def delete_role_from_shop(self, ctx: Context, role: Role):
        delete_shop_roles(ctx.guild.id, role.id)
        await ctx.send(f"Из магазина сервера была удалена роль {role.mention}", delete_after=10)

    @guild_only()
    @check_admin()
    @command(name="set_money")
    async def set_money_user(self, ctx: Context, user: Member, money: int):
        if not user:
            MissingRequiredArgument(user)
            return

        if not money:
            MissingRequiredArgument(money)
            return

        add_money(user.id, ctx.guild.id, money)

        if money > 0:
            await ctx.send(f"{user.mention} получил выплату от администратора в размере {money}", delete_after=10)

        elif money < 0:
            await ctx.send(f"{user.mention} был оштрафован администратором на сумму {money}", delete_after=10)

    @guild_only()
    @check_admin()
    @command(name="set_money_role")
    async def set_money_role(self, ctx: Context, role: Role, money: int):
        async for member in ctx.guild.fetch_members():
            add_money(member.id, ctx.guild.id, money)

        if money > 0:
            await ctx.send(f"Пользователи {role.mention} получили выплату от администратора в размере {money}",
                           delete_after=10)

        elif money < 0:
            await ctx.send(f"Пользователи {role.mention} были оштрафованы администратором на сумму {money}",
                           delete_after=10)

    @guild_only()
    @check_admin()
    @command(name="reset_money")
    async def set_money_role(self, ctx: Context, user: Member):
        reset_money(user.id, ctx.guild.id)

        await ctx.send(f"Пользователь {user.mention} был оштрафован администратором на все деньги",
                       delete_after=10)

    @check_admin()
    @command(name="set_symbol")
    async def set_money(self, ctx: Context, *, symbol: str):
        add_money_symbol(ctx.guild.id, symbol)
        self.bot.money_symbol = symbol
        await ctx.send(f"Был установлен символ валюты {symbol}",
                       delete_after=10)

    @command(name="work_list")
    async def get_work_list(self, ctx: Context):
        work_list_embed = get_work_list_embeds(self.bot)
        await ctx.send(embed=work_list_embed)

    @command(name="work")
    async def work(self, ctx: Context, work_name: str):
        await ctx.send(f'{ctx.author.mention} начал работать на должности "{work_name.title()}". '
                       f"Работа займет некоторое время, ждите",
                       delete_after=10)

        result = await work(ctx.guild, ctx.author, work_name)

        if not result:
            await ctx.send("Что-то пошло не так. Возможно, такой работы нет.",
                           delete_after=10)
            return

        if result > 0:
            embed = good_work_result_embeds(self.bot, ctx.author, result)
            await ctx.send(embed=embed)

        elif result <= 0:
            embed = bad_work_result_embeds(self.bot, ctx.author, result)
            await ctx.send(embed=embed)

    @command(name="slot_machine")
    async def slot_machine(self, ctx: Context, bet: int):
        if get_money(ctx.author.id, ctx.guild.id) - bet >= 0:
            await proceed_slot_machine(ctx, self.bot, ctx.author, bet)
        else:
            await ctx.send("Недостаточно средств на счету", delete_after=10)

    @command(name="transaction")
    async def proceed_transaction(self, ctx: Context, target: Member, amount: int):
        if get_money(ctx.author.id, ctx.guild.id) - amount >= 0:
            withdraw_money(ctx.author.id, ctx.guild.id, amount)
            add_money(target.id, ctx.guild.id, amount)

            embed = transaction_embeds(self.bot.money_symbol, ctx.author, target, amount)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Недостаточно средств на счету", delete_after=10)

    @command(name="to_deposit")
    async def transaction_to_deposit(self, ctx: Context, amount: int):
        if get_money(ctx.author.id, ctx.guild.id) - amount >= 0:
            withdraw_money(ctx.author.id, ctx.guild.id, amount)
            add_money_deposit(ctx.author.id, ctx.guild.id, amount)

            await ctx.send("Перевод прошел успешно", delete_after=10)
        else:
            await ctx.send("Недостаточно средств на счету", delete_after=10)

    @command(name="from_deposit")
    async def transaction_from_deposit(self, ctx: Context, amount: int):
        if get_money_deposit(ctx.author.id, ctx.guild.id) - amount >= 0:
            withdraw_money_deposit(ctx.author.id, ctx.guild.id, amount)
            add_money(ctx.author.id, ctx.guild.id, amount)

            await ctx.send("Перевод прошел успешно", delete_after=10)
        else:
            await ctx.send("Недостаточно средств на счету", delete_after=10)

    @command(name="top10_users")
    async def top10_users(self, ctx: Context):
        embed = await get_top10_users_embeds(ctx.guild, self.bot.money_symbol)
        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_member_remove(self, member: Member):
        delete_user_from_economy(member.id, member.guild.id)


def setup(bot):
    bot.add_cog(EconomyCog(bot))
