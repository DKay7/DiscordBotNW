from utils.db.db_build import with_commit
from utils.db.db_connection import cursor, conn
from config.rating.points_counter import RATING_POINTS_PER_SEC_VOICE, RATING_POINTS_PER_ONE_MESSAGE
from config.rating.rating_to_level import get_level_by_rating


@with_commit
def add_clan_voice_rating_trace(user_id, clan_id, start_time):
    cursor.execute("INSERT OR IGNORE INTO clan_voice_rating_trace VALUES (?, ?, ?)",
                   (user_id, clan_id, start_time))


@with_commit
def remove_clan_voice_rating_trace(user_id, clan_id, end_time):
    start_time = cursor.execute("SELECT StartTime FROM clan_voice_rating_trace "
                                "WHERE (UserID=? AND GroupChannelID=?)",
                                (user_id, clan_id)).fetchone()
    if not start_time:
        print('не удалось получить информацию о времени пользователя в голосовом канале')
        return

    start_time = start_time[0]
    delta_time = end_time - start_time
    delta_rating = int(delta_time.total_seconds() * RATING_POINTS_PER_SEC_VOICE)

    update_clan_rating(user_id, clan_id, delta_rating)

    cursor.execute("DELETE FROM clan_voice_rating_trace "
                   "WHERE (UserID=? AND GroupChannelID=?)", (user_id, clan_id))


def update_clan_message_rating(user_id, clan_id):
    delta_rating = RATING_POINTS_PER_ONE_MESSAGE
    update_clan_rating(user_id, clan_id, delta_rating)


@with_commit
def update_clan_rating(user_id, clan_id, delta_rating):
    temp_level = get_level_by_rating(delta_rating)

    cursor.execute("INSERT INTO clan_rating VALUES (?, ?, ?, ?) "
                   "ON CONFLICT(UserId, GroupChannelId) DO UPDATE "
                   "SET Rating=Rating+?, Level=TO_LEVEL(Rating+?)",
                   (user_id, clan_id, delta_rating, temp_level,
                    delta_rating, delta_rating))


def get_clan_level(user_id, clan_id):
    level = cursor.execute("SELECT Level FROM clan_rating "
                           "WHERE (UserID=? AND GroupChannelId=?)",
                           (user_id, clan_id)).fetchone()

    if level:
        level = level[0]

        return level

    else:
        return 0


def get_clan_level_and_rating(user_id, clan_id):
    entry = cursor.execute("SELECT Rating, Level FROM clan_rating "
                           "WHERE UserID=? AND GroupChannelID=?",
                           (user_id, clan_id)).fetchone()

    if entry:
        rating, level = entry
        return rating, level
    else:
        return 0, 0


def get_clan_position(user_id, clan_id):
    entry = cursor.execute("SELECT RowNum FROM ("
                           "    SELECT ROW_NUMBER() OVER("
                           "            ORDER BY Rating DESC"
                           "     ) RowNum,"
                           "       UserID,"
                           "       GroupChannelId "
                           "    FROM clan_rating "
                           "    WHERE (GroupChannelId=?)"
                           ") "
                           "WHERE (UserID=? AND GroupChannelId=?)",
                           (clan_id, user_id, clan_id)).fetchone()

    if entry:
        position = entry[0]
        return position
    else:
        return "Not found"
