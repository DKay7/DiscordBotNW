from utils.db.db_build import with_commit
from utils.db.db_connection import cursor


@with_commit
def add_marriage_response(user_id, target_id, message_id):
    cursor.execute("INSERT INTO marriage_asks "
                   "(UserId, TargetId, AskerMessageID) "
                   "VALUES(?, ?, ?) "
                   "ON CONFLICT(UserId, TargetId) DO UPDATE "
                   "SET AskerMessageID=?",
                   (user_id, target_id, message_id, message_id))


def has_prev_marriage(user_id, target_id):
    previous_marriage = cursor.execute("SELECT UserId FROM marriage WHERE "
                                       "(TargetId=? OR UserID=? OR TargetId=? OR UserID=?)",
                                       (target_id, user_id, user_id, target_id)).fetchone()

    if previous_marriage:
        return True
    else:
        return False


def find_marriage_response(target_id, message_id):
    user_id = cursor.execute("SELECT UserId FROM marriage_asks "
                             "WHERE (TargetId=? AND AskerMessageID=?)",
                             (target_id, message_id)).fetchone()

    if user_id:
        return user_id[0]


@with_commit
def commit_marriage(user_id, target_id):
    cursor.execute("INSERT INTO marriage (UserID, TargetID) "
                   "VALUES(?, ?)",
                   (user_id, target_id))

    delete_marriage_response(user_id, target_id)


@with_commit
def delete_marriage_response(user_id, target_id):
    cursor.execute("DELETE FROM marriage_asks "
                   "WHERE (UserID=? and TargetID=?) ",
                   (user_id, target_id))


def find_sex_response(target_id, message_id):
    user_id = cursor.execute("SELECT UserID FROM sex_asks "
                             "WHERE (TargetId=? AND AskerMessageID=?)",
                             (target_id, message_id)).fetchone()

    if user_id:
        return user_id[0]


@with_commit
def delete_sex_response(user_id, target_id):
    cursor.execute("DELETE FROM sex_asks "
                   "WHERE (UserID=? and TargetID=?) ",
                   (user_id, target_id))


@with_commit
def add_sex_response(user_id, target_id, message_id):
    cursor.execute("INSERT INTO sex_asks "
                   "(UserID, TargetID, AskerMessageID) "
                   "VALUES(?, ?, ?) "
                   "ON CONFLICT(UserID, TargetID) DO UPDATE "
                   "SET AskerMessageID=?",
                   (user_id, target_id, message_id, message_id))
