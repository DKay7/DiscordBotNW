from discord import Color
from json import loads


def load_file(filename):
    with open(filename, 'r', encoding="utf-8") as file:
        result_dict = loads(file.read())

    return result_dict


def get_message_reactions(filename):
    with open(filename, 'r', encoding="utf-8") as file:
        result_dict = loads(file.read())

    yes = result_dict['yes']
    no = result_dict['no']

    yes_start_index = yes.rfind(":")
    no_start_index = no.rfind(":")

    yes = int(yes[yes_start_index+1:-1])
    no = int(no[no_start_index+1:-1])

    return {"yes": yes, "no": no}


def get_colour(role_config, clan_name):
    if role_config["colour"] == "random":
        return Color.random(seed=role_config["name"].format(clan_name=clan_name))
    else:
        return role_config["colour"]
