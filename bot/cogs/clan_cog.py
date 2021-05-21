from discord.ext.commands import MissingPermissions, guild_only, BadArgument
from discord.ext.commands import Cog, command, Context, MissingRequiredArgument, dm_only
from discord import Member, Reaction, User, Permissions, Guild, PermissionOverwrite
from config.clan.clan_config import CLAN_LEADER_OFFER_MESSAGE_DIR, CLAN_LEADER_ROLE, CLAN_MEMBER_ROLE, CLAN_DEP_ROLE, \
    user_types, channels, CLAN_CHANNELS_PERMS_ROLES_PATTERN
from discord.abc import PrivateChannel
from discord.utils import get

from utils.clan.getters_and_loaders import load_file, get_message_reactions, get_colour


class ClanCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO check permissions_and_roles
    @command(name="choose_leader")
    async def create_choose_leader(self, ctx: Context, prospective_leader: Member):
        if not prospective_leader:
            raise MissingRequiredArgument(prospective_leader)

        # TODO get message text from file
        message_data = load_file(CLAN_LEADER_OFFER_MESSAGE_DIR)
        message = await prospective_leader.send(message_data["text"])

        await message.add_reaction(message_data["yes"])
        await message.add_reaction(message_data["no"])

        # TODO remove next line
        await ctx.send(f"Пользователю {prospective_leader.mention} было отправлено предложение стать лидером")

    @guild_only()
    @command(name="choose_dep")
    async def choose_dep(self, ctx: Context, dep_candidate: Member, clan_name: str):
        if not self._check_leader(ctx.author, clan_name):
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

        leader_role, dep_role, member_role = await self._create_clan_roles(self.bot.guild, clan_name)
        await leader.add_roles(leader_role)
        await self._create_clan_channels(self.bot.guild, (leader_role, dep_role, member_role), clan_name)

        await self.bot.common_rating_channel.set_permissions(leader_role, send_messages=True, read_messages=True)
        await self.bot.wars_channel.set_permissions(leader_role, send_messages=True, read_messages=True)

        await ctx.send(f"Клан `{clan_name}` был удачно создан")

    @Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: User):
        if not user == self.bot.user and isinstance(reaction.message.channel, PrivateChannel):
            reactions = get_message_reactions(CLAN_LEADER_OFFER_MESSAGE_DIR)
            await reaction.message.delete()
            await user.send(f"you've reacted {reaction.emoji}")

            if reaction.emoji.id == reactions["no"]:
                await self.bot.main_channel.send(f"{user.mention} отказался от роли лидера клана")
            elif reaction.emoji.id == reactions['yes']:
                await user.send(f"Создайте клан с помощью команды {self.bot.command_prefix}create_clan <имя клана>.")

    async def _create_clan_roles(self, guild: Guild, clan_name: str):
        leader_role = load_file(CLAN_LEADER_ROLE)
        deputy_leader_role = load_file(CLAN_DEP_ROLE)
        clan_member_role = load_file(CLAN_MEMBER_ROLE)

        leader_role_name = leader_role["name"].format(clan_name=clan_name)
        deputy_leader_role_name = deputy_leader_role["name"].format(clan_name=clan_name)
        clan_member_role_name = clan_member_role["name"].format(clan_name=clan_name)

        leader_role_colour = get_colour(leader_role, clan_name)
        deputy_leader_role_colour = get_colour(deputy_leader_role, clan_name)
        clan_member_role_colour = get_colour(clan_member_role, clan_name)

        leader_role_perms = Permissions(**leader_role["permissions"])
        deputy_leader_role_perms = Permissions(**deputy_leader_role["permissions"])
        clan_member_role_perms = Permissions(**clan_member_role["permissions"])

        leader_role = await guild.create_role(name=leader_role_name,
                                              colour=leader_role_colour,
                                              permissions=leader_role_perms)
        dep_role = await guild.create_role(name=deputy_leader_role_name,
                                           colour=deputy_leader_role_colour,
                                           permissions=deputy_leader_role_perms)
        member_role = await guild.create_role(name=clan_member_role_name,
                                              colour=clan_member_role_colour,
                                              permissions=clan_member_role_perms)

        return tuple((leader_role, dep_role, member_role))

    async def _create_clan_channels(self, guild: Guild, clan_roles: tuple, clan_name: str):
        assert len(clan_roles) == len(user_types)
        perms_overwrites = {guild.default_role: PermissionOverwrite(read_messages=False)}
        clan_category = await guild.create_category(f"Clan {clan_name}", overwrites=perms_overwrites)

        for channel_key, channel in channels.items():
            for index, user_type in enumerate(user_types.values()):
                perms = load_file(CLAN_CHANNELS_PERMS_ROLES_PATTERN.format(user_type=user_type, channel_type=channel))

                perms_overwrites.update({clan_roles[index]: PermissionOverwrite(**perms)})

            if "voice" in channel_key:
                await guild.create_voice_channel(f"{channel}_{clan_name}",
                                                 overwrites=perms_overwrites,
                                                 category=clan_category)
            else:
                await guild.create_text_channel(f"{channel}_{clan_name}",
                                                overwrites=perms_overwrites,
                                                category=clan_category)

    def _check_leader(self, leader: Member, clan_name: str):
        pass_check = False

        for role in leader.roles:
            role_name = role.name.lower()
            if "leader" in role_name and clan_name.lower() in role_name \
               and "dep" not in role_name:
                pass_check = True
                break

        return pass_check


def setup(bot):
    bot.add_cog(ClanCog(bot))
