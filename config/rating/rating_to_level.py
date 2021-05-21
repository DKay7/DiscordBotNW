import math


def get_level_by_rating(rating):
    level = int(math.log2(rating + 1e-5))
    return level if level > 0 else 0


def get_rating_for_next_level(level):
    rating = int(2 ** level)
    return rating
