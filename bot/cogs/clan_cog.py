from discord.ext.commands import MissingPermissions, guild_only, BadArgument
from discord.ext.commands import Cog, command, Context, MissingRequiredArgument, dm_only
from discord import Member, Reaction, User
from config.clan.clan_config import CLAN_LEADER_OFFER_MESSAGE_PATH, CLAN_DEP_ROLE, CLAN_LEADER_OFFER_REACTIONS_PATH
from discord.abc import PrivateChannel
from discord.utils import get

from utils.clan.checkers import check_leader
from utils.clan.creators import create_clan_roles, create_clan_channels
from utils.common.utils import load_file


class ClanCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO check permissions_and_roles
    @command(name="choose_leader")
    async def create_choose_leader(self, ctx: Context, prospective_leader: Member):
        if not prospective_leader:
            raise MissingRequiredArgument(prospective_leader)

        # TODO get message text from file
        message_text = load_file(CLAN_LEADER_OFFER_MESSAGE_PATH)["text"]
        message = await prospective_leader.send(message_text)

        reactions = load_file(CLAN_LEADER_OFFER_REACTIONS_PATH)
        await message.add_reaction(reactions["yes"])
        await message.add_reaction(reactions["no"])

        # TODO remove next line
        await ctx.send(f"Пользователю {prospective_leader.mention} было отправлено предложение стать лидером")

    @guild_only()
    @command(name="choose_dep")
    async def choose_dep(self, ctx: Context, dep_candidate: Member, clan_name: str):
        if not check_leader(ctx.author, clan_name):
            raise MissingPermissions("leader role")

        role_name = load_file(CLAN_DEP_ROLE)["name"].format(clan_name=clan_name)
        dep_role = get(self.bot.guild.roles, name=role_name)

        if not dep_role:
            raise BadArgument

        if dep_role in dep_candidate.roles:
            await ctx.send(f"{dep_candidate.mention} уже заместитель клана {clan_name}")

        await dep_candidate.add_roles(dep_role)
        await ctx.send(f"Пользователь {dep_candidate.mention} был назначен заместителем клана {clan_name}")

    @dm_only()
    @command(name="create_clan")
    async def create_new_clan(self, ctx: Context, *, clan_name: str):
        leader = self.bot.guild.get_member(ctx.author.id)
        if not leader:
            await ctx.send(f"Вы не являетесь членом сервера и не можете создавать кланы")
            return

        leader_role, dep_role, member_role = await create_clan_roles(self.bot.guild, clan_name)
        await leader.add_roles(leader_role)
        await create_clan_channels(self.bot.guild, (leader_role, dep_role, member_role), clan_name)

        await self.bot.common_rating_channel.set_permissions(leader_role, send_messages=True, read_messages=True)
        await self.bot.wars_channel.set_permissions(leader_role, send_messages=True, read_messages=True)

        await ctx.send(f"Клан `{clan_name}` был удачно создан")

    @Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: User):
        if not user.bot and isinstance(reaction.message.channel, PrivateChannel):

            reactions = load_file(CLAN_LEADER_OFFER_REACTIONS_PATH)
            await reaction.message.clear_reaction(reactions['yes'])
            await reaction.message.clear_reaction(reactions['no'])
            await user.send(f"Вы выбрали {reaction.emoji}")

            if str(reaction.emoji) == reactions["no"]:
                await self.bot.main_channel.send(f"{user.mention} отказался от роли лидера клана")
            elif str(reaction.emoji) == reactions['yes']:
                await user.send(f"Создайте клан с помощью команды {self.bot.command_prefix}create_clan <имя клана>.")


def setup(bot):
    bot.add_cog(ClanCog(bot))
