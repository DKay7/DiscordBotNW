from discord.ext.commands import BadArgument, Converter
from datetime import timedelta, datetime
from discord import NotFound, Object
from discord.utils import find


class BannedUser(Converter):
    async def convert(self, ctx, arg):
        if ctx.guild.me.guild_permissions.ban_members:
            if arg.isdigit():
                try:
                    return (await ctx.guild.fetch_ban(Object(id=int(arg)))).user
                except NotFound:
                    raise BadArgument

            banned_users = [e.user for e in await ctx.guild.bans()]
            if banned_users:
                if (user := find(lambda u: str(u) == arg[1:] or str(u) == arg, banned_users)) is not None:
                    return user
                else:
                    await ctx.send(f"Пользователь не найден среди забаненных")
                    raise BadArgument
            else:
                await ctx.send(f"Список забаненных пользователей пуст")
                raise BadArgument


class TimeConverter(Converter):
    def __init__(self):
        self.minutes = 0
        self.hours = 0
        self.delta = timedelta()
        self.end_date = datetime.utcnow()

    async def convert(self, _, arg):
        time_type = arg[-1]

        if time_type not in ['h', 'm'] or not (arg := arg[:-1]).isdigit():
            raise BadArgument

        if time_type == 'h':
            self.hours = int(arg)
        elif time_type == 'm':
            self.minutes = int(arg)

        self.delta = timedelta(hours=self.hours, minutes=self.minutes)
        self.end_date = datetime.utcnow() + self.delta

        return self

    def __str__(self):
        return f"{self.hours} час., {self.minutes} мин."

    def get_end_time(self):
        return self.end_date

    def get_seconds(self) -> float:
        return self.delta.total_seconds()
