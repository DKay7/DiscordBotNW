from json import loads
from config.utilities_commands.commands_data import GIFS_PATH


def load_gifs_file():
    with open(GIFS_PATH, "r") as file:
        gifs_dict = loads(file.read())

    return gifs_dict
