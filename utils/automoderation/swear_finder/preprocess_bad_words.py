
def preprocess_bad_words(bad_words_path):
    with open(bad_words_path, "r") as file:
        bad_words_list = file.read()

    bad_words_list = set(bad_words_list.split("\n"))
    bad_words_list = list(sorted(bad_words_list))

    with open(bad_words_path, "w") as file:
        file.write("\n".join(bad_words_list))

    return bad_words_list
