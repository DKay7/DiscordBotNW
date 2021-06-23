from config.rating.rating_stat_image import USER_NAME_X_L, USER_NAME_Y, STAT_SIZE, STAT_X_L, STAT_Y, USER_NAME_COLOR
from config.rating.rating_stat_image import IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_USERNAME_FONT, USER_NAME_SIZE, STAT_COLOR
from config.rating.rating_stat_image import RATING_STAT_BACKGROUND, LEFT_X_PB, BOTTOM_Y_PB, WIDTH_PB, HEIGHT_PB
from config.rating.rating_stat_image import POS_SIZE, POS_COLOR, POS_X_L, POS_X_R, POS_Y, CORNERS_RADIUS_AV
from config.rating.rating_stat_image import BACKGROUND_PB, FOREGROUND_PB, AVATAR_SIZE, CORNERS_RADIUS_IM
from config.rating.points_counter import RATING_POINTS_PER_ONE_MESSAGE, RATING_POINTS_PER_SEC_VOICE
from config.rating.rating_stat_image import STAT_X_R, USER_NAME_X_R, IMAGE_STAT_FONT
from config.rating.rating_to_level import get_rating_for_next_level
from utils.db.rating.rating import get_level_and_rating, get_position
from utils.db.rating.clan_rating import get_clan_level_and_rating, get_clan_position
from PIL import Image, ImageFont, ImageDraw
from math import log10, ceil
from discord import Member, Guild, CategoryChannel
from io import BytesIO


def draw_progress_bar_shape(image_draw, x_left, y_bottom, height, width, color):
    image_draw.ellipse((x_left, y_bottom,
                        x_left + height, y_bottom + height),
                       fill=color)

    image_draw.rectangle((x_left + height / 2, y_bottom,
                          x_left + width + height / 2, y_bottom + height),
                         fill=color)

    image_draw.ellipse((x_left + width, y_bottom,
                        x_left + width + height, y_bottom + height),
                       fill=color)


def draw_progress_bar(backdrop, current, total):
    image_draw = ImageDraw.Draw(backdrop)
    draw_progress_bar_shape(image_draw, LEFT_X_PB, BOTTOM_Y_PB, HEIGHT_PB, WIDTH_PB, BACKGROUND_PB)

    foreground_width = WIDTH_PB * (current / total)
    draw_progress_bar_shape(image_draw, LEFT_X_PB, BOTTOM_Y_PB, HEIGHT_PB, foreground_width, FOREGROUND_PB)

    return backdrop


def add_corners(image, radius):
    circle = Image.new('L', (radius * 2, radius * 2), 0)
    image_draw = ImageDraw.Draw(circle)
    image_draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)
    alpha = Image.new('L', image.size, 255)

    w, h = image.size
    alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
    alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
    alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
    alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))
    image.putalpha(alpha)
    return image


async def get_round_avatar(user: Member):
    avatar_url = user.avatar_url_as(size=128)
    avatar_bytes = BytesIO(await avatar_url.read())
    avatar_img = Image.open(avatar_bytes)
    avatar_img = avatar_img.resize((AVATAR_SIZE, AVATAR_SIZE))
    avatar_img = add_corners(avatar_img, CORNERS_RADIUS_AV)

    return avatar_img


def get_sized_font(box_x_left, box_x_right, text, font_path, start_size):
    font_size = start_size
    font = ImageFont.truetype(font_path, start_size, encoding='utf-8')

    while font.getsize(text)[0] >= (box_x_right - box_x_left):
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)

    return font


def add_text(image, user: Member, current, total, level, position):
    image_draw = ImageDraw.Draw(image)

    user_name_text = user.display_name
    user_name_font = get_sized_font(USER_NAME_X_L, USER_NAME_X_R, user_name_text, IMAGE_USERNAME_FONT, USER_NAME_SIZE)
    image_draw.text((USER_NAME_X_L, USER_NAME_Y), user_name_text, USER_NAME_COLOR, font=user_name_font)

    stat_exp_text = f"{current} / {total} Exp"
    stat_exp_font = get_sized_font(STAT_X_L, STAT_X_R, stat_exp_text, IMAGE_STAT_FONT, STAT_SIZE)
    image_draw.text((STAT_X_L, STAT_Y), stat_exp_text, STAT_COLOR, font=stat_exp_font)

    stat_lvl_text = f"{level} Lvl"
    stat_lvl_y = max(POS_Y, stat_exp_font.getsize(stat_exp_text)[1] + STAT_Y)
    stat_lvl_font = get_sized_font(STAT_X_L, STAT_X_R, stat_lvl_text, IMAGE_STAT_FONT, STAT_SIZE)
    image_draw.text((STAT_X_L, stat_lvl_y), stat_lvl_text, STAT_COLOR, font=stat_lvl_font)

    stat_pos_text = f"#{position}"
    stat_pos_y = max(POS_Y, user_name_font.getsize(user_name_text)[1] + STAT_Y)
    stat_pos_font = get_sized_font(POS_X_L, POS_X_R, stat_pos_text, IMAGE_STAT_FONT, POS_SIZE)
    image_draw.text((POS_X_L, stat_pos_y), stat_pos_text, POS_COLOR, font=stat_pos_font)


def get_stat_for_user(user: Member, guild: Guild):
    rating, level = get_level_and_rating(user.id, guild.id)
    total_rating = get_rating_for_next_level(level + 1)
    position = get_position(user.id, guild.id)

    n_digits = ceil(max(abs(log10(RATING_POINTS_PER_ONE_MESSAGE)),
                        abs(log10(RATING_POINTS_PER_SEC_VOICE))))

    rating = round(rating, n_digits)
    return rating, total_rating, level, position


def get_clan_stat_for_user(user: Member, clan: CategoryChannel):
    rating, level = get_clan_level_and_rating(user.id, clan.id)
    total_rating = get_rating_for_next_level(level + 1)
    position = get_clan_position(user.id, clan.id)

    n_digits = ceil(max(abs(log10(RATING_POINTS_PER_ONE_MESSAGE)),
                        abs(log10(RATING_POINTS_PER_SEC_VOICE))))

    rating = round(rating, n_digits)
    return rating, total_rating, level, position


async def draw_stat_image(user: Member, stats: tuple):
    current_rating, total_rating, level, position = stats

    backdrop = Image.open(RATING_STAT_BACKGROUND)
    backdrop.resize((IMAGE_WIDTH, IMAGE_HEIGHT))
    avatar_img = await get_round_avatar(user)

    draw_progress_bar(backdrop, current_rating, total_rating)
    backdrop.paste(avatar_img, (0, 0), avatar_img)
    backdrop = add_corners(backdrop, CORNERS_RADIUS_IM)
    add_text(backdrop, user, current_rating, total_rating, level, position)
    return backdrop
