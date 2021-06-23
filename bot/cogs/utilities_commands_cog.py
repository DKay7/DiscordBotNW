from discord import Member, Reaction
from discord.ext.commands import Cog, command, Greedy, BadArgument, MissingRequiredArgument, Context
from typing import Optional

from discord.ext.commands.core import guild_only

from config.utilities_commands.commands_data import ACTIONS
from utils.utilities_commands.embeds import get_avatar_embeds, get_utilities_embeds, get_marriages_embeds
from utils.utilities_commands.embeds import get_sex_embeds, get_user_info_embeds, get_server_info_embeds
from utils.utilities_commands.loaders import load_gifs_file
from utils.db.utilities_commands import add_marriage_response, has_prev_marriage, add_sex_response
from random import choice
from config.utilities_commands.marriage import MARRIAGE_REACTIONS_PATH
from config.utilities_commands.sex import SEX_REACTIONS_PATH
from utils.common.utils import load_file
from utils.utilities_commands.marriage import check_marriage_answer_and_reply
from utils.utilities_commands.sex import check_sex_answer_and_reply


class UtilsCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @guild_only()
    @command(name="get_avatar")
    async def get_avatar(self, ctx: Context, user: Optional[Member]):
        user = user or ctx.author
        avatar_embed = get_avatar_embeds(user)
        await ctx.send(embed=avatar_embed)

    @guild_only()
    @command(name="utilities", aliases=list(ACTIONS.keys()))
    async def utilities(self, ctx: Context, users: Greedy[Member]):
        users.append(ctx.author)
        command_name = ctx.invoked_with
        command_data = ACTIONS.get(command_name, None)
        gifs = load_gifs_file().get(command_name, None)

        if not command_data or not gifs or command_data[0] != len(users):
            raise BadArgument

        _, result_message = command_data
        gif_link = choice(gifs)

        mentioned_users = list(map(lambda u: u.mention, users))
        result_message = result_message.format(*reversed(mentioned_users))

        avatar_embed = get_utilities_embeds(result_message, gif_link)
        await ctx.send(embed=avatar_embed)

    @guild_only()
    @command(name="marriage")
    async def ask_marriage(self, ctx: Context, user: Member):
        if not user:
            raise MissingRequiredArgument(user)

        if has_prev_marriage(ctx.author.id, user.id):
            await ctx.send(f"У вас или у {user.mention} уже есть зарегистрированный брак")
            return

        marriage_embed = get_marriages_embeds(ctx.author, user, type_="ask")
        message = await ctx.send(embed=marriage_embed)

        add_marriage_response(ctx.author.id, user.id, message.id)

        reactions = load_file(MARRIAGE_REACTIONS_PATH)
        await message.add_reaction(reactions["yes"])
        await message.add_reaction(reactions["no"])

    @guild_only()
    @command(name="sex")
    async def ask_sex(self, ctx: Context, user: Member):
        if not user:
            raise MissingRequiredArgument(user)

        sex_embed = get_sex_embeds(ctx.author, user, type_="ask")
        message = await ctx.send(embed=sex_embed)

        add_sex_response(ctx.author.id, user.id, message.id)

        reactions = load_file(SEX_REACTIONS_PATH)
        await message.add_reaction(reactions["yes"])
        await message.add_reaction(reactions["no"])

    @guild_only()
    @command(name="userinfo")
    async def get_userinfo(self, ctx: Context, user: Optional[Member]):
        user = user or ctx.author
        embed = get_user_info_embeds(user, ctx.guild)
        await ctx.send(embed=embed)

    @guild_only()
    @command(name="serverinfo")
    async def get_serverinfo(self, ctx: Context):
        embed = get_server_info_embeds(ctx.guild)
        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: Member):

        if not user.bot:
            await check_marriage_answer_and_reply(self.bot, reaction, user)
            await check_sex_answer_and_reply(self.bot, reaction, user)


def setup(bot):
    bot.add_cog(UtilsCog(bot))
