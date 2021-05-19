from .db_build_utils import with_commit
from .db_connection import cursor, conn
from config.rating_config import RATING_POINTS_PER_SEC_VOICE, RATING_POINTS_PER_ONE_MESSAGE, get_level_by_rating


conn.create_function("TO_LEVEL", 1, get_level_by_rating)


@with_commit
def add_voice_rating_trace(user_id, guild_id, start_time):
    cursor.execute("INSERT OR IGNORE INTO voice_rating_trace VALUES (?, ?, ?)", (user_id, guild_id, start_time))


@with_commit
def remove_voice_rating_trace(user_id, guild_id, end_time):
    start_time = cursor.execute("SELECT StartTime FROM voice_rating_trace "
                                "WHERE (UserID=? AND GuildID=?)", (user_id, guild_id)).fetchone()
    if not start_time:
        print('не удалось получить информацию о времени пользователя в голосовом канале')
        return

    start_time = start_time[0]
    delta_time = end_time - start_time
    delta_rating = int(delta_time.total_seconds() * RATING_POINTS_PER_SEC_VOICE)

    update_rating(user_id, guild_id, delta_rating)

    cursor.execute("DELETE FROM voice_rating_trace "
                   "WHERE (UserID=? AND GuildID=?)", (user_id, guild_id))


def update_message_rating(user_id, guild_id):
    delta_rating = RATING_POINTS_PER_ONE_MESSAGE
    update_rating(user_id, guild_id, delta_rating)


@with_commit
def update_rating(user_id, guild_id, delta_rating):
    temp_level = get_level_by_rating(delta_rating)

    cursor.execute("INSERT INTO rating VALUES (?, ?, ?, ?) "
                   "ON CONFLICT(UserID, GuildID) DO UPDATE "
                   "SET Rating=Rating+?, Level=TO_LEVEL(Rating+?)",
                   (user_id, guild_id, delta_rating, temp_level,
                    delta_rating, delta_rating))


def get_level(user_id, guild_id):
    level = cursor.execute("SELECT Level FROM rating "
                           "WHERE (UserID=? AND GuildID=?)", (user_id, guild_id)).fetchone()

    if level:
        level = level[0]

        return level
