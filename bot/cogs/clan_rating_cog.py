from discord import ChannelType, Member, File
from discord.ext.commands import Cog, command
from discord.ext.commands.core import guild_only

from utils.common.checkers import check_user_in_clan
from utils.db.clans import get_all_clan_ids
from utils.db.rating.clan_rating import update_clan_message_rating, remove_clan_voice_rating_trace, get_clan_level
from utils.db.rating.clan_rating import add_clan_voice_rating_trace
from config.rating.restricted import restricted_guilds, restricted_channels

from datetime import datetime
from config.bot.bot_config import PREFIX
from utils.rating.checkers import check_clan_level_and_get_role
from utils.rating.progress_bar import draw_stat_image, get_clan_stat_for_user
from io import BytesIO
from typing import Optional


class ClanRatingCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message):
        if message.channel.type != ChannelType.private \
                and not message.content.startswith(PREFIX) \
                and not message.author.bot \
                and message.channel.id not in restricted_channels \
                and message.guild.id not in restricted_guilds:

            if message.channel.category.id not in get_all_clan_ids():
                return

            user = message.author
            guild = message.guild
            clan = message.channel.category

            current_level = get_clan_level(user.id, clan.id)
            update_clan_message_rating(user.id, clan.id)
            await check_clan_level_and_get_role(user, guild, clan, current_level)

    @Cog.listener()
    async def on_voice_state_update(self, member, state_before, state_after):

        channel = state_after.channel or state_before.channel
        guild = channel.guild

        if state_before.channel != state_after.channel \
                and guild.id not in restricted_guilds:

            if not state_before.channel and state_after.channel.category.id in get_all_clan_ids():
                # TODO remove next line
                print("Клан Подключился",  state_after.channel)
                add_clan_voice_rating_trace(member.id, state_after.channel.category.id, datetime.utcnow())

            elif state_after.channel and state_before.channel:
                if state_after.channel.category.id not in get_all_clan_ids() and \
                        state_before.channel.category.id in get_all_clan_ids():

                    current_level = get_clan_level(member.id, state_before.channel.category.id)
                    remove_clan_voice_rating_trace(member.id, state_before.channel.category.id, datetime.utcnow())
                    await check_clan_level_and_get_role(member, state_before.channel.guild,
                                                        state_before.channel.category, current_level)
                    # TODO remove next line
                    print("Клан Отключился, перейдя вовне", state_after.channel)

                elif state_before.channel.category.id not in get_all_clan_ids() and \
                        state_after.channel.category.id in get_all_clan_ids():
                    add_clan_voice_rating_trace(member.id, state_after.channel.category.id, datetime.utcnow())
                    # TODO remove next line
                    print("Клан Подключился, перейдя извне", state_before.channel)

                elif state_before.channel.category.id in get_all_clan_ids() and \
                        state_after.channel.category.id in get_all_clan_ids():
                    # TODO remove next line
                    print("переключился в другой клан", state_after.channel)
                    add_clan_voice_rating_trace(member.id, state_after.channel.category.id, datetime.utcnow())

                    current_level = get_clan_level(member.id, state_before.channel.category.id)
                    remove_clan_voice_rating_trace(member.id, state_before.channel.category.id, datetime.utcnow())
                    await check_clan_level_and_get_role(member, state_before.channel.guild,
                                                        state_before.channel.category, current_level)

            elif not state_after.channel and state_before.channel and \
                    state_before.channel.category.id in get_all_clan_ids():

                # TODO remove next line
                print("Клан Отключился", state_before.channel)
                current_level = get_clan_level(member.id, state_before.channel.category.id)
                remove_clan_voice_rating_trace(member.id, state_before.channel.category.id, datetime.utcnow())
                await check_clan_level_and_get_role(member, state_before.channel.guild,
                                                    state_before.channel.category, current_level)

    @guild_only()
    @command(name="clan_rating")
    async def clan_rating(self, ctx, user: Optional[Member]):
        user = user or ctx.author
        clan = ctx.channel.category

        if check_user_in_clan(user, ctx.channel.category):
            stats = get_clan_stat_for_user(user, clan)
            image = await draw_stat_image(user, stats)
            with BytesIO() as image_binary:
                image.save(image_binary, 'PNG')
                image_binary.seek(0)
                await ctx.send(file=File(fp=image_binary, filename=f'{clan}_{user}_rating.png'))
        else:
            await ctx.send("Вы не состоите в клане, либо запускаете команду не из кланового чата",
                           delete_after=10)


def setup(bot):
    bot.add_cog(ClanRatingCog(bot))
