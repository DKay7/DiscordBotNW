from utils.db.db_utilities_commands import find_marriage_response, commit_marriage, delete_marriage_response
from utils.common.utils import load_file
from config.utilities_commands.marriage import MARRIAGE_REACTIONS_PATH
from utils.utilities_commands.embeds import get_marriages_embeds


async def check_marriage_answer_and_reply(bot, reaction, user):
    reactions = load_file(MARRIAGE_REACTIONS_PATH)
    channel = reaction.message.channel

    if str(reaction.emoji) not in reactions.values():
        return

    elif str(reaction.emoji) == reactions['yes']:
        asker_id = find_marriage_response(user.id, reaction.message.id)

        if not asker_id:
            await channel.send(f"Этот пользователь не предлагал вам обручиться с ним", delete_after=10)

        else:
            await reaction.message.clear_reaction(reactions['yes'])
            await reaction.message.clear_reaction(reactions['no'])
            await channel.send(f"Вы выбрали {reaction.emoji}")

            commit_marriage(user.id, asker_id)
            asker = bot.guild.get_member(asker_id)

            embed = get_marriages_embeds(asker, user, type_="confirm")
            await channel.send(embed=embed)

    elif str(reaction.emoji) == reactions['no']:
        asker_id = find_marriage_response(user.id, reaction.message.id)

        if not asker_id:
            await channel.send(f"Этот пользователь не предлагал вам обручиться с ним", delete_after=10)

        else:
            await reaction.message.clear_reaction(reactions['yes'])
            await reaction.message.clear_reaction(reactions['no'])
            await reaction.message.channel.send(f"Вы выбрали {reaction.emoji}")

            delete_marriage_response(user.id, asker_id)
            asker = bot.guild.get_member(asker_id)

            embed = get_marriages_embeds(asker, user, type_="deny")
            await channel.send(embed=embed)
