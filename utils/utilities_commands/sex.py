from utils.db.utilities_commands import find_sex_response,  delete_sex_response
from utils.common.utils import load_file
from config.utilities_commands.sex import SEX_REACTIONS_PATH
from utils.utilities_commands.embeds import get_sex_embeds


async def check_sex_answer_and_reply(bot, reaction, user):
    reactions = load_file(SEX_REACTIONS_PATH)
    channel = reaction.message.channel

    if str(reaction.emoji) not in reactions.values():
        return

    elif str(reaction.emoji) == reactions['yes']:
        asker_id = find_sex_response(user.id, reaction.message.id)

        if not asker_id:
            await channel.send(f"Этот пользователь не предлагал вам заняться с ним сексом", delete_after=10)

        else:
            await reaction.message.clear_reaction(reactions['yes'])
            await reaction.message.clear_reaction(reactions['no'])
            await channel.send(f"Вы выбрали {reaction.emoji}")

            asker = bot.guild.get_member(asker_id)
            embed = get_sex_embeds(asker, user, type_="confirm")
            await channel.send(embed=embed)

    elif str(reaction.emoji) == reactions['no']:
        asker_id = find_sex_response(user.id, reaction.message.id)

        if not asker_id:
            await channel.send(f"Этот пользователь не предлагал вам заняться с ним сексом", delete_after=10)

        else:
            await reaction.message.clear_reaction(reactions['yes'])
            await reaction.message.clear_reaction(reactions['no'])
            await reaction.message.channel.send(f"Вы выбрали {reaction.emoji}")

            delete_sex_response(user.id, asker_id)
            asker = bot.guild.get_member(asker_id)

            embed = get_sex_embeds(asker, user, type_="deny")
            await channel.send(embed=embed)
