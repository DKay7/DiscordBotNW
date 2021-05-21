from discord import ChannelType, Member, File
from discord.ext.commands import Cog, command
from utils.db.db_rating_utils import add_voice_rating_trace, remove_voice_rating_trace, update_message_rating
from config.rating.restricted import restricted_guilds, restricted_rating_channels
from utils.rating.checkers import check_level_and_get_role
from datetime import datetime
from config.bot.bot_config import PREFIX
from utils.rating.progress_bar import draw_stat_image
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
                and message.channel.id not in restricted_rating_channels \
                and message.guild.id not in restricted_guilds:

            user_id = message.author.id
            guild_id = message.guild.id
            update_message_rating(user_id, guild_id)
            await check_level_and_get_role(message.author, message.guild)

    @Cog.listener()
    async def on_voice_state_update(self, member, state_before, state_after):

        channel = state_after.channel or state_before.channel
        guild = channel.guild

        if state_before.channel != state_after.channel \
                and guild.id not in restricted_guilds:

            if not state_before.channel:
                # TODO remove next line
                print("Подключился")
                add_voice_rating_trace(member.id, state_after.channel.guild.id, datetime.utcnow())

            elif (not state_after.channel) and state_before.channel:
                # TODO remove next line
                print("Отключился", state_before.channel)
                remove_voice_rating_trace(member.id, state_before.channel.guild.id, datetime.utcnow())
                await check_level_and_get_role(member, state_before.channel.guild)

    @command()
    async def rating(self, ctx, user: Optional[Member]):
        user = user or ctx.author
        guild = ctx.guild

        image = await draw_stat_image(user, guild)
        with BytesIO() as image_binary:
            image.save(image_binary, 'PNG')
            image_binary.seek(0)
            await ctx.send(file=File(fp=image_binary, filename=f'{guild}_{user}_rating.png'))


def setup(bot):
    bot.add_cog(RatingCog(bot))
