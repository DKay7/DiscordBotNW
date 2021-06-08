from json import loads


def load_file(filename):
    with open(filename, 'r', encoding="utf-8") as file:
        result_dict = loads(file.read())

    return result_dict
