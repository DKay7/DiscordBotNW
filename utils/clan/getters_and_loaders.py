from discord import Color


def get_colour(role_config, clan_name):
    if role_config["colour"] == "random":
        return Color.random(seed=role_config["name"].format(clan_name=clan_name))

    return role_config["colour"]
