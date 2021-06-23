from discord.ext.commands import MissingPermissions, guild_only, has_permissions
from discord.ext.commands import Cog, command, Context, MissingRequiredArgument, dm_only
from discord import Member, Reaction, User
from discord.abc import PrivateChannel, GuildChannel
from utils.clan.embeds import get_offer_embeds_and_reactions, get_top10_clans_embed, get_duel_ask_embeds
from utils.clan.checkers import check_leader
from utils.clan.creators import create_clan_roles, create_clan_channels
from utils.db.clans import add_clan_response, write_win, add_duel_response
from utils.db.clan_economy import get_clan_money, withdraw_clan_money
from utils.clan.reaction_listeners import clan_leader_offer_reaction_listener, clan_dep_leader_offer_reaction_listener, \
    duel_reactions_listener
from utils.clan.reaction_listeners import clan_member_offer_reaction_listener
from utils.common.checkers import check_admin, check_user_in_clan


class ClanCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO check permissions_and_roles
    @guild_only()
    @command(name="choose_leader")
    async def choose_leader(self, ctx: Context, prospective_leader: Member):
        if not prospective_leader:
            raise MissingRequiredArgument(prospective_leader)

        offer_embed, reactions = get_offer_embeds_and_reactions(type_="leader")
        message = await prospective_leader.send(embed=offer_embed)

        add_clan_response(target_id=prospective_leader.id, type_="leader",
                          guild_id=ctx.guild.id, message_id=message.id,
                          channel_id=ctx.channel.id)

        await message.add_reaction(reactions["yes"])
        await message.add_reaction(reactions["no"])

        # TODO remove next line
        await ctx.send(f"Пользователю {prospective_leader.mention} было отправлено предложение стать лидером",
                       delete_after=10)

    @guild_only()
    @command(name="choose_dep")
    async def choose_dep(self, ctx: Context, dep_candidate: Member, clan_name: str):
        if not check_leader(ctx.author, clan_name):
            raise MissingPermissions("leader role")

        offer_embed, reactions = get_offer_embeds_and_reactions(type_="dep_leader", clan_name=clan_name)
        message = await dep_candidate.send(embed=offer_embed)

        add_clan_response(target_id=dep_candidate.id, type_="dep_leader", guild_id=ctx.guild.id,
                          clan_name=clan_name, message_id=message.id,
                          channel_id=ctx.channel.id)

        await message.add_reaction(reactions["yes"])
        await message.add_reaction(reactions["no"])

        # TODO remove next line
        await ctx.send(f"Пользователю {dep_candidate.mention} было отправлено предложение стать заместителем лидера "
                       f"клана `{clan_name}`",
                       delete_after=10)

    @guild_only()
    @command(name="invite")
    async def invite(self, ctx: Context, member_candidate: Member, clan_name: str):
        if not check_leader(ctx.author, clan_name):
            raise MissingPermissions("leader role")

        offer_embed, reactions = get_offer_embeds_and_reactions(type_="member", clan_name=clan_name)
        message = await member_candidate.send(embed=offer_embed)

        add_clan_response(target_id=member_candidate.id, type_="member", guild_id=ctx.guild.id,
                          clan_name=clan_name, message_id=message.id,
                          channel_id=ctx.channel.id)

        await message.add_reaction(reactions["yes"])
        await message.add_reaction(reactions["no"])

        # TODO remove next line
        await ctx.send(f"Пользователю {member_candidate.mention} было отправлено предложение стать участником "
                       f"клана `{clan_name}`",
                       delete_after=10)

    @dm_only()
    @command(name="create_clan")
    async def create_new_clan(self, ctx: Context, *, clan_name: str):

        guild = self.bot.guild
        leader = guild.get_member(ctx.author.id)

        if not leader:
            await ctx.send(f"Вы не являетесь членом сервера и не можете создавать кланы")
            return

        leader_role, dep_role, member_role = await create_clan_roles(guild, clan_name)
        await leader.add_roles(leader_role)
        await create_clan_channels(guild, (leader_role, dep_role, member_role), clan_name)

        await self.bot.common_rating_channel.set_permissions(leader_role, send_messages=True, read_messages=True)
        await self.bot.wars_channel.set_permissions(leader_role, send_messages=True, read_messages=True)

        await self.bot.common_text_channel.set_permissions(leader_role, send_messages=True, read_messages=True)
        await self.bot.common_text_channel.set_permissions(dep_role, send_messages=True, read_messages=True)
        await self.bot.common_text_channel.set_permissions(member_role, send_messages=True, read_messages=True)

        await ctx.send(f"Клан `{clan_name}` был удачно создан", delete_after=10)

    @guild_only()
    @check_admin()
    @has_permissions(manage_roles=True, ban_members=True)
    @command(name="win")
    async def confirm_win(self, ctx: Context, *, clan_name: str):
        num_affected_rows = write_win(clan_name)

        if num_affected_rows:
            await ctx.send(f"Клану `{clan_name}` была засчитана одна победа.",
                           delete_after=10)
        else:
            await ctx.send(f"Что-то пошло не так. Возможно, такого клана нет.",
                           delete_after=10)

    @guild_only()
    @command(name="top10")
    async def get_top10(self, ctx: Context):
        top10_embed = get_top10_clans_embed()

        await ctx.send(embed=top10_embed)

    @guild_only()
    @command(name="duel")
    async def call_duel(self, ctx: Context, opponent: Member, bet: int):
        if check_user_in_clan(ctx.author, ctx.channel.category) and \
           check_user_in_clan(opponent, ctx.channel.category):

            asker_money = get_clan_money(ctx.author.id, ctx.channel.category.id)

            if asker_money - bet < 0:
                await ctx.send(f"У вас недостаточно денег, чтобы сделать такую ставку",
                               delete_after=10)
                return

            withdraw_clan_money(ctx.author.id, ctx.channel.category.id, bet)
            duel_embeds, reactions = get_duel_ask_embeds(ctx.author, opponent)

            message = await ctx.send(embed=duel_embeds)
            add_duel_response(ctx.author.id, opponent.id, message.id, bet)

            await message.add_reaction(reactions["yes"])
            await message.add_reaction(reactions["no"])

        else:
            await ctx.send(f"Вы или ваш соперник не состоите в клане, "
                           f"либо запускаете команду не в канале клана",
                           delete_after=10)
            return

    @Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: User):
        if not user.bot and isinstance(reaction.message.channel, PrivateChannel):

            await reaction.message.delete()
            await user.send(f"Вы выбрали {reaction.emoji}")

            await clan_leader_offer_reaction_listener(reaction, user, self.bot)
            await clan_dep_leader_offer_reaction_listener(reaction, user, self.bot)
            await clan_member_offer_reaction_listener(reaction, user, self.bot)

        elif not user.bot and isinstance(reaction.message.channel, GuildChannel):
            await duel_reactions_listener(reaction, user, self.bot)


def setup(bot):
    bot.add_cog(ClanCog(bot))
