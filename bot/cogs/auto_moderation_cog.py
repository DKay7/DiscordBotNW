from emoji import UNICODE_EMOJI_ENGLISH
from re import findall
from typing import List
from datetime import datetime
from config.automoderation.common import MESSAGES_TO_WATCH, DELAY_SECONDS, SIMILARITY, URL_REGEXP, EMOJI_REGEXP
from config.automoderation.restricted import automod_restricted_guilds, automod_restricted_channels, \
    automod_restricted_users, automod_restricted_roles
from config.automoderation.temp_ban_config import AUTO_TEMPBAN_REASON, TIME_TO_AUTO_TEMPBAN
from utils.automoderation.swear_finder import cython_swear_finder
from discord.ext.commands import Cog
from discord import Message, ChannelType
from difflib import SequenceMatcher

from utils.automoderation.embeds import get_emoji_warn_embeds, get_url_warn_embeds, get_swear_warn_embeds, \
    get_mention_warn_embeds, get_uppercase_warn_embeds, get_similarity_warn_embeds
from utils.mod.warn_commands import warn_user_util


class AutoMod(Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def _delete_messages(messages: List[Message]):
        for message in messages:
            await message.delete()

    async def _mentions_check(self, user_message: Message):
        def _check(cached_message: Message):
            return user_message.author == cached_message.author \
                    and len(user_message.mentions) \
                    and (datetime.utcnow() - user_message.created_at).seconds < DELAY_SECONDS

        messages = list(filter(lambda message: _check(message), self.bot.cached_messages))

        if len(messages) >= MESSAGES_TO_WATCH:
            return messages[:-1]

    async def _swear_check(self, user_message: Message):
        def _check(cached_message: Message):
            return user_message.author == cached_message.author \
                   and cython_swear_finder.contains_bad_words(cached_message.content) \
                   and (datetime.utcnow() - user_message.created_at).seconds < DELAY_SECONDS

        messages = list(filter(lambda message: _check(message), self.bot.cached_messages))

        if messages:
            return messages

    async def _url_check(self, user_message: Message):
        def _check(cached_message: Message):
            return user_message.author == cached_message.author \
                   and findall(URL_REGEXP, cached_message.content) \
                   and (datetime.utcnow() - user_message.created_at).seconds < DELAY_SECONDS

        messages = list(filter(lambda message: _check(message), self.bot.cached_messages))

        if messages:
            return messages

    async def _emoji_check(self, user_message: Message):
        def _check(cached_message: Message):
            return user_message.author == cached_message.author \
                   and (findall(EMOJI_REGEXP, cached_message.content)
                        or set(cached_message.content) & set(UNICODE_EMOJI_ENGLISH)) \
                   and (datetime.utcnow() - user_message.created_at).seconds < DELAY_SECONDS

        messages = list(filter(lambda message: _check(message), self.bot.cached_messages))

        if len(messages) >= MESSAGES_TO_WATCH:
            return messages[:-1]

    async def _uppercase_check(self, user_message: Message):
        def _check(cached_message: Message):
            return user_message.author == cached_message.author \
                   and cached_message.content.isupper() \
                   and (datetime.utcnow() - user_message.created_at).seconds < DELAY_SECONDS

        messages = list(filter(lambda message: _check(message), self.bot.cached_messages))

        if len(messages) >= MESSAGES_TO_WATCH:
            return messages[:-1]

    async def _similarity_check(self, user_message: Message):
        def _check(cached_message: Message):
            return user_message.author == cached_message.author \
                   and (datetime.utcnow() - user_message.created_at).seconds < DELAY_SECONDS

        user_messages = list(filter(lambda message: _check(message), self.bot.cached_messages))[-MESSAGES_TO_WATCH:]

        if len(user_messages) >= MESSAGES_TO_WATCH:
            similarities = []
            for index in range(0, len(user_messages[:-1]), 1):
                m_1 = user_messages[index]
                m_2 = user_messages[index + 1]
                similarity = SequenceMatcher(None,
                                             m_1.content.lower().strip(),
                                             m_2.content.lower().strip()).quick_ratio()

                if similarity > SIMILARITY:
                    if m_1 not in similarities:
                        similarities.append(m_1)
                    if m_2 not in similarities:
                        similarities.append(m_2)

            return similarities[:-1] if len(similarities) >= MESSAGES_TO_WATCH else False

        return False

    @Cog.listener()
    async def on_message(self, message):

        if message.channel.type is ChannelType.text \
                and not any(map(lambda role: role.id in automod_restricted_roles, message.author.roles)) \
                and message.channel.guild.id not in automod_restricted_guilds \
                and message.channel.id not in automod_restricted_channels \
                and message.author.id not in automod_restricted_users \
                and not message.author.bot \
                and not message.content.startswith(self.bot.command_prefix):

            if messages_to_delete := await self._url_check(message):
                await self._delete_messages(messages_to_delete)
                embed = get_url_warn_embeds(message.author)
                await message.author.send(embed=embed)

                await warn_user_util(message.author, AUTO_TEMPBAN_REASON,
                                     self.bot, message.channel.guild,
                                     message.channel, TIME_TO_AUTO_TEMPBAN)

                # TODO remove next line
                await message.channel.send("Здесь нельзя делиться ссылками",
                                           delete_after=10)

            elif await self._swear_check(message):
                await message.delete()
                embed = get_swear_warn_embeds(message.author)
                await message.author.send(embed=embed)

                await warn_user_util(message.author, AUTO_TEMPBAN_REASON,
                                     self.bot, message.channel.guild,
                                     message.channel, TIME_TO_AUTO_TEMPBAN)

                # TODO remove next line
                await message.channel.send("Здесь нельзя использовать такую лексику",
                                           delete_after=10)

            elif messages_to_delete := await self._mentions_check(message):
                await self._delete_messages(messages_to_delete)
                embed = get_mention_warn_embeds(message.author)
                await message.author.send(embed=embed)

                await warn_user_util(message.author, AUTO_TEMPBAN_REASON,
                                     self.bot, message.channel.guild,
                                     message.channel, TIME_TO_AUTO_TEMPBAN)

                # TODO remove next line
                await message.channel.send("Вы пишете слишком много сообщений c упоминаниями",
                                           delete_after=10)

            elif messages_to_delete := await self._uppercase_check(message):
                await self._delete_messages(messages_to_delete)
                embed = get_uppercase_warn_embeds(message.author)
                await message.author.send(embed=embed)

                await warn_user_util(message.author, AUTO_TEMPBAN_REASON,
                                     self.bot, message.channel.guild,
                                     message.channel, TIME_TO_AUTO_TEMPBAN)

                # TODO remove next line
                await message.channel.send("Вы пишете слишком много сообщений в верхнем регистре",
                                           delete_after=10)
            elif messages_to_delete := await self._similarity_check(message):
                await self._delete_messages(messages_to_delete)
                embed = get_similarity_warn_embeds(message.author)
                await message.author.send(embed=embed)

                await warn_user_util(message.author, AUTO_TEMPBAN_REASON,
                                     self.bot, message.channel.guild,
                                     message.channel, TIME_TO_AUTO_TEMPBAN)

                # TODO remove next line
                await message.channel.send("Вы пишете слишком много одинаковых сообщений",
                                           delete_after=10)

            elif messages_to_delete := await self._emoji_check(message):
                await self._delete_messages(messages_to_delete)
                embed = get_emoji_warn_embeds(message.author)
                await message.author.send(embed=embed)

                await warn_user_util(message.author, AUTO_TEMPBAN_REASON,
                                     self.bot, message.channel.guild,
                                     message.channel, TIME_TO_AUTO_TEMPBAN)

                # TODO remove next line
                await message.channel.send("Вы пишете слишком много сообщений cо смайликами",
                                           delete_after=10)


def setup(bot):
    bot.add_cog(AutoMod(bot))
