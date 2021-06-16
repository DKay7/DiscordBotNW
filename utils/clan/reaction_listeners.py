from utils.clan.duel import proceed_duel, deny_duel
from utils.common.utils import load_file
from config.clan.reactions_path import CLAN_LEADER_OFFER_REACTIONS_PATH, CLAN_DEP_LEADER_OFFER_REACTIONS_PATH
from config.clan.reactions_path import CLAN_MEMBER_OFFER_REACTIONS_PATH, DUEL_ASK_REACTIONS_PATH
from config.clan.roles import CLAN_MEMBER_ROLE, CLAN_DEP_ROLE
from utils.db.clans import get_clan_name_from_response, delete_clan_response, get_channel_id_from_response
from utils.db.clans import add_duel_response, delete_duel_response, find_duel_response
from utils.db.clan_economy import get_money, withdraw_money
from discord.ext.commands import BadArgument
from discord.utils import get


async def clan_leader_offer_reaction_listener(reaction, user, bot):
    reactions = load_file(CLAN_LEADER_OFFER_REACTIONS_PATH)

    if str(reaction.emoji) in reactions.values():
        channel_id = get_channel_id_from_response(target_id=user.id, message_id=reaction.message.id,
                                                  type_="leader")
        channel = bot.guild.get_channel(channel_id)

        if str(reaction.emoji) == reactions["no"]:
            await channel.send(f"{user.mention} отказался от роли лидера клана",
                               delete_after=10)

        elif str(reaction.emoji) == reactions['yes']:
            await channel.send(f"{user.mention} согласился стать лидером клана. Ждем, пока он настроит свой клан",
                               delete_after=10)
            await user.send(f"Создайте клан с помощью команды {bot.command_prefix}create_clan <имя клана>.")

        delete_clan_response(target_id=user.id, guild_id=bot.guild.id, type_="leader")


async def clan_dep_leader_offer_reaction_listener(reaction, user, bot):
    reactions = load_file(CLAN_DEP_LEADER_OFFER_REACTIONS_PATH)

    if str(reaction.emoji) in reactions.values():
        clan_name = get_clan_name_from_response(target_id=user.id, type_="dep_leader",
                                                message_id=reaction.message.id)
        channel_id = get_channel_id_from_response(target_id=user.id, message_id=reaction.message.id,
                                                  type_="dep_leader")
        channel = bot.guild.get_channel(channel_id)

        if str(reaction.emoji) == reactions["no"]:
            await channel.send(f"{user.mention} отказался от роли заместителя лидера клана {clan_name}")

        elif str(reaction.emoji) == reactions['yes']:
            role_name = load_file(CLAN_DEP_ROLE)["name"].format(clan_name=clan_name)
            dep_role = get(bot.guild.roles, name=role_name)
            user = get(bot.guild.members, id=user.id)

            if not dep_role or not user:
                raise BadArgument

            if dep_role in user.roles:
                return

            await user.add_roles(dep_role)
            await channel.send(f"Пользователь {user.mention} был назначен заместителем лидера клана {clan_name}",
                               delete_after=10)

            delete_clan_response(target_id=user.id, guild_id=bot.guild.id,
                                 clan_name=clan_name, type_="dep_leader")


async def clan_member_offer_reaction_listener(reaction, user, bot):
    reactions = load_file(CLAN_MEMBER_OFFER_REACTIONS_PATH)

    if str(reaction.emoji) in reactions.values():
        clan_name = get_clan_name_from_response(target_id=user.id, type_="member",
                                                message_id=reaction.message.id)
        channel_id = get_channel_id_from_response(target_id=user.id, message_id=reaction.message.id,
                                                  type_="member")
        channel = bot.guild.get_channel(channel_id)

        if str(reaction.emoji) == reactions['yes']:
            role_name = load_file(CLAN_MEMBER_ROLE)["name"].format(clan_name=clan_name)
            member_role = get(bot.guild.roles, name=role_name)
            user = get(bot.guild.members, id=user.id)

            if not member_role or not user:
                raise BadArgument

            if member_role in user.roles:
                return

            await user.add_roles(member_role)
            await channel.send(f"Пользователь {user.mention} был включен в клан {clan_name}",
                               delete_after=10)

        elif str(reaction.emoji) == reactions['no']:
            await channel.send(f"{user.mention} отказался вступать в клан {clan_name}")

        delete_clan_response(target_id=user.id, guild_id=bot.guild.id,
                             clan_name=clan_name, type_="member")


async def duel_reactions_listener(reaction, user, bot):
    reactions = load_file(DUEL_ASK_REACTIONS_PATH)
    channel = reaction.message.channel

    if str(reaction.emoji) in reactions.values():
        entry = find_duel_response(user.id, reaction.message.id)

        if not entry:
            await channel.send(f"Этот пользователь не вызывал вас на дуэль", delete_after=10)
            return

        asker_id, bet = entry

        await reaction.message.clear_reaction(reactions['yes'])
        await reaction.message.clear_reaction(reactions['no'])
        await channel.send(f"Вы выбрали {reaction.emoji}")

        asker = bot.guild.get_member(asker_id)

        if str(reaction.emoji) == reactions['yes']:
            await proceed_duel(asker, user, bet, channel)

        elif str(reaction.emoji) == reactions['no']:
            await deny_duel(asker, user, bet, channel)

