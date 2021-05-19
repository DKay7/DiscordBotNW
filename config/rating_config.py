import math


def get_level_by_rating(rating):
    level = int(math.log2(rating + 1e-5))
    return level if level > 0 else 0


RATING_POINTS_PER_SEC_VOICE = 1 / 5
RATING_POINTS_PER_ONE_MESSAGE = 1 / 5
NUM_LEVELS_FOR_NEXT_ROLE = 5

NEW_LEVEL_ROLE_MESSAGE_TEXT = r"data/messages/new_level_role_congrats.json"

MAX_LEVEL_ROLE_ID = 844171664081813564

roles_per_levels = {
    5: 844167909064048641,
    10: 844169143544053770,
}

restricted_guilds = [620004833960787968]
restricted_rating_channels = [838150502402883585]
