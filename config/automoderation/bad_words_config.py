from utils.automoderation.swear_finder.preprocess_bad_words import preprocess_bad_words

BAD_WORDS_PATH = r"data/text_files/bad_words.txt"
BAD_WORDS_LIST = preprocess_bad_words(BAD_WORDS_PATH)
