from discord import ChannelType
from discord.ext.commands import Cog, command
from utils.db.db_rating_utils import add_voice_rating_trace, remove_voice_rating_trace, update_message_rating
from config.rating_config import restricted_rating_channels, restricted_guilds
from utils.rating_utils.checkers import check_level_and_get_role
from datetime import datetime
from config.bot_config import PREFIX


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
                and guild not in restricted_guilds:

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
    async def test(self, ctx):
        await ctx.message.author.send('👋')


def setup(bot):
    bot.add_cog(RatingCog(bot))
