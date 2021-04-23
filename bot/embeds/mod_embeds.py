from discord import Embed


def get_temp_ban_embed(duration, link):
    invite_embed = Embed(colour=0xFF0000)
    invite_embed.add_field(name="Информация",
                           value=f"Вы были временно забанены на сервере на `{duration}` сек. "
                                 f"По истечении этого времени, "
                                 f"вы сможете снова присоединиться к серверу по [сслыке]({link})")

    invite_embed.add_field(name="Время бана", value=f"`{duration}` сек.")
    invite_embed.add_field(name="Ссылка для возвращения", value=f"[Клик!]({link})")