from discord import ChannelType, Member, File
from discord.ext.commands import Cog, command
from discord.ext.commands.core import guild_only

from utils.db.clans import get_all_clan_ids
from utils.db.rating.rating import add_voice_rating_trace, remove_voice_rating_trace, update_message_rating, get_level
from config.rating.restricted import restricted_guilds, restricted_channels
from utils.rating.checkers import check_level_and_get_role
from datetime import datetime
from config.bot.bot_config import PREFIX
from utils.rating.progress_bar import draw_stat_image, get_stat_for_user
from io import BytesIO
from typing import Optional


class RatingCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message):
        if message.channel.type != ChannelType.private \
                and not message.content.startswith(PREFIX) \
                and not message.author.bot \
                and message.channel.id not in restricted_channels \
                and message.guild.id not in restricted_guilds:

            if message.channel.category.id in get_all_clan_ids():
                return

            user_id = message.author.id
            guild_id = message.guild.id

            current_level = get_level(user_id, guild_id)
            update_message_rating(user_id, guild_id)
            await check_level_and_get_role(message.author, message.guild, current_level)

    @Cog.listener()
    async def on_voice_state_update(self, member, state_before, state_after):

        channel = state_after.channel or state_before.channel
        guild = channel.guild

        if state_before.channel != state_after.channel \
                and guild.id not in restricted_guilds:

            if not state_before.channel and state_after.channel.category.id not in get_all_clan_ids():
                # TODO remove next line
                print("Подключился",  state_after.channel)
                add_voice_rating_trace(member.id, state_after.channel.guild.id, datetime.utcnow())

            elif state_after.channel and state_before.channel:
                if state_after.channel.category.id in get_all_clan_ids() and \
                        state_before.channel.category.id not in get_all_clan_ids():

                    current_level = get_level(member.id,  state_before.channel.guild.id)
                    remove_voice_rating_trace(member.id, state_before.channel.guild.id, datetime.utcnow())
                    await check_level_and_get_role(member, state_before.channel.guild, current_level)
                    # TODO remove next line
                    print("Отключился, перейдя в клан", state_after.channel)

                elif state_before.channel.category.id in get_all_clan_ids() and \
                        state_after.channel.category.id not in get_all_clan_ids():
                    add_voice_rating_trace(member.id, state_after.channel.guild.id, datetime.utcnow())
                    # TODO remove next line
                    print("Подключился, перейдя из клана", state_before.channel)

            elif not state_after.channel and state_before.channel and \
                    state_before.channel.category.id not in get_all_clan_ids():

                # TODO remove next line
                print("Отключился", state_before.channel)

                current_level = get_level(member.id, state_before.channel.guild.id)
                remove_voice_rating_trace(member.id, state_before.channel.guild.id, datetime.utcnow())
                await check_level_and_get_role(member, state_before.channel.guild, current_level)

    @guild_only()
    @command(name="rating")
    async def rating(self, ctx, user: Optional[Member]):
        user = user or ctx.author
        guild = ctx.guild

        stats = get_stat_for_user(user, guild)
        image = await draw_stat_image(user, stats)
        with BytesIO() as image_binary:
            image.save(image_binary, 'PNG')
            image_binary.seek(0)
            await ctx.send(file=File(fp=image_binary, filename=f'{guild}_{user}_rating.png'))


def setup(bot):
    bot.add_cog(RatingCog(bot))
